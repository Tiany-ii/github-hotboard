# -*- coding: utf-8 -*-
"""
GitHub 热榜 · 桌面版外壳
--------------------------------
在本地起一个只读 HTTP 服务（127.0.0.1），用 WebView2 加载单文件应用。

界面来源优先级（重要）：
  1) exe 同目录的  web/github-hot.html   —— 放这里可以热更新界面，不用重新打包
  2) exe 同目录的  github-hot.html
  3) exe 内置的那一份（打包时嵌入，作为兜底）
这样改界面只需要替换一个 HTML 文件；只有改动 Python 侧能力时才需要重新打包。
"""
import os
import re
import sys
import time
import shutil
import socket
import zipfile
import tempfile
import threading
import http.server
import urllib.request
import urllib.parse

APP_TITLE = "GitHub Hotboard"
APP_FILE = "github-hot.html"
__version__ = "1.1.1"
PORT_FROM, PORT_TO = 8765, 8785

INDEX_PATH = ""
INDEX_SOURCE = ""


def app_version():
    """以界面里的 APP_VERSION 为唯一来源，避免两处版本号漂移。"""
    try:
        with open(resolve_index()[0], "r", encoding="utf-8") as f:
            head = f.read(200000)
        m = re.search(r'APP_VERSION\s*=\s*"([^"]+)"', head)
        if m:
            return m.group(1)
    except Exception:
        pass
    return __version__


def resource_dir():
    """PyInstaller 打包后资源在 _MEIPASS，源码运行时在脚本目录。"""
    if getattr(sys, "frozen", False):
        return getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


def resolve_index():
    """按优先级找出要加载的 HTML，返回 (路径, 来源说明)。"""
    candidates = []
    if getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(sys.executable)
        candidates.append((os.path.join(exe_dir, "web", APP_FILE), "外部 web/ 目录"))
        candidates.append((os.path.join(exe_dir, APP_FILE), "exe 同目录"))
    else:
        here = os.path.dirname(os.path.abspath(__file__))
        candidates.append((os.path.join(here, "web", APP_FILE), "本地 web/ 目录"))
        candidates.append((os.path.join(here, APP_FILE), "脚本同目录"))
    candidates.append((os.path.join(resource_dir(), APP_FILE), "内置版本"))

    for path, label in candidates:
        if os.path.isfile(path):
            return path, label
    raise SystemExit("找不到 %s" % APP_FILE)


def storage_dir():
    """便携模式：exe 同级存在 portable.txt 或 data 文件夹时，数据放在 data/ 里。
    这样整个文件夹拷到别的电脑，关注列表、曲线、译文都跟着走。"""
    if getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(sys.executable)
        data_dir = os.path.join(exe_dir, "data")
        if os.path.exists(os.path.join(exe_dir, "portable.txt")) or os.path.isdir(data_dir):
            os.makedirs(data_dir, exist_ok=True)
            # 首次便携启动：把旧的 %LOCALAPPDATA% 数据搬过来，避免"看起来全丢了"
            legacy = os.path.join(os.environ.get("LOCALAPPDATA") or "", "GitHubHot")
            try:
                empty = not os.listdir(data_dir)
            except OSError:
                empty = False
            if empty and os.path.isdir(legacy):
                try:
                    shutil.copytree(legacy, data_dir, dirs_exist_ok=True)
                    # 旧目录若留有崩溃标记，不要让它把刚拷来的配置清掉
                    try:
                        os.remove(os.path.join(data_dir, ".running"))
                    except OSError:
                        pass
                except Exception:
                    pass
            return data_dir

    root = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    path = os.path.join(root, "GitHubHot")
    os.makedirs(path, exist_ok=True)
    return path


def strict_free(p):
    """严格检测：Windows 上 SO_REUSEADDR 允许抢占已被监听的端口，
    所以这里不设它，bind 失败才说明真的有人在用。"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("127.0.0.1", p))
            return True
        except OSError:
            return False


def loose_free(p):
    """宽松检测：端口刚被释放时可能还处于 TIME_WAIT，允许复用。"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind(("127.0.0.1", p))
            return True
        except OSError:
            return False


def is_our_instance(p):
    """端口上跑的是不是本程序（用于「重复双击」时聚焦已有窗口）。"""
    try:
        import urllib.request
        with urllib.request.urlopen("http://127.0.0.1:%d/%s" % (p, APP_FILE), timeout=1.5) as r:
            return "GitHub 热榜".encode("utf-8") in r.read(8192)
    except Exception:
        return False


def focus_existing():
    try:
        import ctypes
        u = ctypes.windll.user32
        u.FindWindowW.restype = ctypes.c_void_p
        h = u.FindWindowW(None, APP_TITLE)
        if h:
            u.ShowWindow(h, 9)
            u.SetForegroundWindow(h)
            return True
    except Exception:
        pass
    return False


def choose_port():
    """固定用 8765：localStorage 按「协议+主机+端口」隔离，换端口就等于换了一套数据。
    返回 -1 表示「已经有一个自己在跑」。"""
    # 先看是不是重复双击：端口上如果是本程序，直接交给上层聚焦
    if is_our_instance(PORT_FROM):
        return -1
    for _ in range(12):
        if strict_free(PORT_FROM):
            return PORT_FROM
        time.sleep(0.25)
    # 端口刚释放、还在 TIME_WAIT 的情况，允许复用
    if loose_free(PORT_FROM):
        return PORT_FROM
    return None


class Handler(http.server.BaseHTTPRequestHandler):
    """只对外提供这一个 HTML 文件，不做目录浏览，避免暴露同目录的其它文件。"""

    server_version = "GHHot/1.1"

    def do_GET(self):
        if self.path.split("?")[0] not in ("/", "/" + APP_FILE):
            self.send_error(404)
            return
        try:
            with open(INDEX_PATH, "rb") as f:
                body = f.read()
        except OSError:
            self.send_error(500)
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def log_message(self, fmt, *args):
        pass


class QuietServer(http.server.ThreadingHTTPServer):
    daemon_threads = True

    def handle_error(self, request, client_address):
        pass  # 客户端提前断开时不要刷屏


def start_server(port):
    httpd = QuietServer(("127.0.0.1", port), Handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


def log_path():
    if getattr(sys, "frozen", False):
        return os.path.join(os.path.dirname(sys.executable), "selftest.log")
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "selftest.log")


def log(msg):
    try:
        with open(log_path(), "a", encoding="utf-8") as f:
            f.write("%s %s\n" % (time.strftime("%H:%M:%S"), msg))
    except Exception:
        pass
    try:
        print(msg)
    except Exception:
        pass


# =========================================================
# 下载器：由页面通过 pywebview.api 调用
# =========================================================
ALLOWED_HOSTS = ("github.com", "codeload.github.com", "objects.githubusercontent.com",
                 "api.github.com", "raw.githubusercontent.com")


def default_download_dir():
    home = os.path.expanduser("~")
    for name in ("Downloads", "下载"):
        p = os.path.join(home, name)
        if os.path.isdir(p):
            return p
    return home


def safe_name(name):
    bad = '\\/:*?"<>|'
    out = "".join(("_" if c in bad else c) for c in str(name)).strip(" .")
    reserved = {"CON", "PRN", "AUX", "NUL"} | {"COM%d" % i for i in range(1, 10)} | {"LPT%d" % i for i in range(1, 10)}
    if out.upper() in reserved:
        out = "_" + out
    return out[:120] or "download"


def unique_path(path):
    if not os.path.exists(path):
        return path
    base, ext = os.path.splitext(path)
    for i in range(2, 100):
        cand = "%s-%d%s" % (base, i, ext)
        if not os.path.exists(cand):
            return cand
    return "%s-%d%s" % (base, int(time.time()), ext)


class DownloadCanceled(Exception):
    pass


class Downloader:
    """一个极简的下载队列：一次可以跑多个任务，页面轮询进度。"""

    def __init__(self):
        self.jobs = {}
        self.lock = threading.Lock()
        self.seq = 0

    # ---------- 供 JS 调用 ----------
    def pick_folder(self, start=""):
        try:
            import webview
            win = webview.windows[0] if webview.windows else None
            if not win:
                return {"ok": False, "error": "窗口还没准备好"}
            start = start if start and os.path.isdir(start) else default_download_dir()
            r = win.create_file_dialog(webview.FOLDER_DIALOG, directory=start)
            if not r:
                return {"ok": True, "path": ""}
            return {"ok": True, "path": r[0]}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def default_dir(self):
        try:
            return {"ok": True, "path": default_download_dir()}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def check_dir(self, path):
        try:
            os.makedirs(path, exist_ok=True)
            return {"ok": True, "path": path}
        except Exception as e:
            return {"ok": False, "error": "目录不可用：%s" % e}

    def start(self, url, dest, name, kind="file", sub=""):
        url = str(url or "")
        host = urllib.parse.urlparse(url).hostname or ""
        if host not in ALLOWED_HOSTS:
            return {"ok": False, "error": "只允许从 GitHub 下载（当前域名 %s）" % (host or "空")}
        if not os.path.isdir(dest):
            try:
                os.makedirs(dest, exist_ok=True)
            except OSError as e:
                return {"ok": False, "error": "无法写入目录：%s" % e}

        self.seq += 1
        jid = "d%d" % self.seq
        job = {"id": jid, "state": "downloading", "got": 0, "total": 0, "speed": 0,
               "name": safe_name(name), "dest": dest, "kind": kind, "sub": safe_name(sub) if sub else "",
               "path": "", "error": "", "cancel": False, "started": time.time()}
        with self.lock:
            self.jobs[jid] = job
        threading.Thread(target=self._run, args=(jid, url), daemon=True).start()
        return {"ok": True, "id": jid}

    def progress(self, jid):
        with self.lock:
            job = self.jobs.get(jid)
            if not job:
                return {"ok": False, "error": "任务不存在"}
            return {"ok": True, "state": job["state"], "got": job["got"], "total": job["total"],
                    "speed": job["speed"], "path": job["path"], "error": job["error"],
                    "name": job["name"]}

    def cancel(self, jid):
        with self.lock:
            job = self.jobs.get(jid)
            if job:
                job["cancel"] = True
        return {"ok": True}

    def open_folder(self, path):
        try:
            if path and os.path.isdir(path):
                os.startfile(path)
                return {"ok": True}
            return {"ok": False, "error": "目录不存在：%s" % path}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # ---------- 内部 ----------
    def _set(self, jid, **kw):
        with self.lock:
            if jid in self.jobs:
                self.jobs[jid].update(kw)

    def _run(self, jid, url):
        job = self.jobs.get(jid)
        if not job:
            return
        part = os.path.join(job["dest"], ".%s.part" % job["name"])
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "GitHubHot/1.2 (+local app)",
                "Accept": "application/octet-stream",
            })
            with urllib.request.urlopen(req, timeout=30) as r:
                total = int(r.headers.get("Content-Length") or 0)
                self._set(jid, total=total)
                got, mark, mark_t = 0, 0, time.time()
                with open(part, "wb") as f:
                    while True:
                        if self.jobs.get(jid, {}).get("cancel"):
                            raise DownloadCanceled()
                        chunk = r.read(262144)
                        if not chunk:
                            break
                        f.write(chunk)
                        got += len(chunk)
                        now = time.time()
                        if now - mark_t >= 0.4:
                            self._set(jid, got=got, speed=int((got - mark) / (now - mark_t)))
                            mark, mark_t = got, now
                self._set(jid, got=got, speed=0)

            if self.jobs.get(jid, {}).get("cancel"):
                raise DownloadCanceled()

            final = os.path.join(job["dest"], job["name"])
            if job["kind"] == "zip" and zipfile.is_zipfile(part):
                self._set(jid, state="unzipping")
                final = self._unzip(part, job["dest"], job["sub"] or job["name"].replace(".zip", ""))
                try:
                    os.remove(part)
                except OSError:
                    pass
            else:
                final = unique_path(final)
                os.replace(part, final)

            self._set(jid, state="done", path=final, speed=0)
        except DownloadCanceled:
            try:
                os.remove(part)
            except OSError:
                pass
            self._set(jid, state="canceled", speed=0)
        except Exception as e:
            try:
                os.remove(part)
            except OSError:
                pass
            self._set(jid, state="error", error=self._friendly(e), speed=0)

    @staticmethod
    def _friendly(e):
        msg = str(e)
        if isinstance(e, urllib.error.HTTPError):
            if e.code == 404:
                return "下载地址不存在（可能换了默认分支或删了 release）"
            if e.code == 403:
                return "被 GitHub 限流了，过一会儿再试"
            return "GitHub 返回 %d" % e.code
        if isinstance(e, urllib.error.URLError):
            return "网络连接失败：%s" % (getattr(e, "reason", msg),)
        if isinstance(e, OSError) and getattr(e, "errno", None) == 28:
            return "磁盘空间不足"
        return msg or "下载失败"

    def _unzip(self, part, dest, folder_name):
        tmp = tempfile.mkdtemp(prefix="ghhot-", dir=dest)
        try:
            with zipfile.ZipFile(part) as z:
                z.extractall(tmp)
            entries = [e for e in os.listdir(tmp) if not e.startswith("__MACOSX")]
            target = unique_path(os.path.join(dest, safe_name(folder_name)))
            if len(entries) == 1 and os.path.isdir(os.path.join(tmp, entries[0])):
                os.replace(os.path.join(tmp, entries[0]), target)
            else:
                os.makedirs(target, exist_ok=True)
                for e in entries:
                    os.replace(os.path.join(tmp, e), os.path.join(target, e))
            return target
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


def main():
    global INDEX_PATH, INDEX_SOURCE

    if "--version" in sys.argv or "-V" in sys.argv:
        try:
            INDEX_PATH, INDEX_SOURCE = resolve_index()
        except SystemExit:
            pass
        print("%s %s" % (APP_TITLE, app_version()))
        return

    INDEX_PATH, INDEX_SOURCE = resolve_index()

    port = choose_port()
    if port == -1:
        focus_existing()
        log("程序已在运行，已聚焦已有窗口")
        return
    if port is None:
        for p in range(PORT_FROM + 1, PORT_TO):
            if port_free(p):
                port = p
                break
        if port is None:
            log("端口 %d~%d 全部被占用，无法启动" % (PORT_FROM, PORT_TO))
            return

    start_server(port)
    url = "http://127.0.0.1:%d/%s" % (port, APP_FILE)
    if port != PORT_FROM:
        url += "#altport=%d" % port

    # ---------- 无界面自检 ----------
    if "--selftest" in sys.argv:
        import urllib.request
        with urllib.request.urlopen(url, timeout=10) as r:
            body = r.read().decode("utf-8", "ignore")
        log("selftest v%s port=%d bytes=%d source=%s title=%s" %
            (app_version(), port, len(body), INDEX_SOURCE, "GitHub Hotboard" in body))
        return

    store = storage_dir()

    if "--where" in sys.argv:
        log("storage=%s portable=%s" % (store, os.path.basename(store) == "data"))
        return

    # ---------- 下载功能自检（无界面） ----------
    if "--selftest-dl" in sys.argv:
        d = Downloader()
        target = os.path.join(tempfile.gettempdir(), "ghhot-dltest")
        shutil.rmtree(target, ignore_errors=True)
        os.makedirs(target, exist_ok=True)
        url = "https://codeload.github.com/octocat/Hello-World/zip/refs/heads/master"
        r = d.start(url, target, "Hello-World.zip", "zip", "Hello-World")
        if not r.get("ok"):
            log("selftest-dl start failed: %s" % r.get("error"))
            return
        jid = r["id"]
        for _ in range(120):
            time.sleep(0.5)
            st = d.progress(jid)
            if st.get("state") in ("done", "error", "canceled"):
                break
        log("selftest-dl state=%s got=%s total=%s path=%s err=%s" %
            (st.get("state"), st.get("got"), st.get("total"), st.get("path"), st.get("error")))
        if st.get("path") and os.path.isdir(st["path"]):
            log("selftest-dl files=%s" % os.listdir(st["path"]))
        shutil.rmtree(target, ignore_errors=True)
        return

    # 浏览器内核配置损坏（白屏、打不开）时的修复入口：
    # 改名而不是删除，数据还在，确认没用可以手动删掉
    if "--reset" in sys.argv:
        prof = os.path.join(store, "EBWebView")
        if os.path.isdir(prof):
            bak = prof + ".old-" + time.strftime("%Y%m%d-%H%M%S")
            try:
                os.rename(prof, bak)
                log("已重置浏览器配置，原目录保留为 %s" % bak)
            except OSError as e:
                log("重置失败：%s" % e)
        else:
            log("没有需要重置的浏览器配置：%s" % prof)
        return

    # ---------- 异常退出检测（只记录，绝不清空数据） ----------
    # 这里以前会在发现 .running 时 rmtree 整个数据目录，那会把 localStorage
    # 里的关注列表、译文、API Key 一起删掉。现在只记录，配置真的坏了用 --reset。
    flag = os.path.join(store, ".running")
    if os.path.exists(flag):
        log("上次未正常退出（强制结束或崩溃），本次继续使用现有配置")
    try:
        with open(flag, "w", encoding="utf-8") as f:
            f.write(str(os.getpid()))
    except Exception:
        pass

    os.environ.setdefault("WEBVIEW2_USER_DATA_FOLDER", store)

    import webview

    # --debug：打开开发者工具，改 HTML 时能看报错、查 DOM、改样式
    debug = "--debug" in sys.argv

    downloader = Downloader()

    window = webview.create_window(
        APP_TITLE, url,
        js_api=downloader,
        width=1480, height=950,
        min_size=(1000, 640),
        text_select=True,
    )
    shown = {"ok": False}

    def on_shown():
        shown["ok"] = True

    window.events.shown += on_shown

    # ---------- 带界面自检 ----------
    if "--selftest-gui" in sys.argv:
        def probe(win):
            last = None
            for i in range(20):
                time.sleep(1.5)
                try:
                    rows = win.evaluate_js('document.querySelectorAll("#tbTop tr").length')
                    title = win.evaluate_js('document.title')
                    api = win.evaluate_js('(window.pywebview && window.pywebview.api) ? Object.keys(window.pywebview.api).join(",") : "NONE"')
                    log("gui-selftest rows=%s title=%s api=%s shown=%s wait=%.1fs"
                        % (rows, title, api, shown["ok"], (i + 1) * 1.5))
                    last = None
                    break
                except Exception as e:
                    last = e
            if last is not None:
                log("gui-selftest failed: %r shown=%s" % (last, shown["ok"]))
            try:
                win.destroy()
            except Exception:
                pass

        webview.start(probe, window, gui="edgechromium", debug=debug,
                      private_mode=False, storage_path=store)
        if shown["ok"]:
            try:
                os.remove(flag)
            except OSError:
                pass
        return

    if debug:
        log("debug 模式：界面来源=%s 端口=%d（右键可打开检查器）" % (INDEX_SOURCE, port))

    webview.start(gui="edgechromium", private_mode=False, storage_path=store, debug=debug)

    # 正常关闭才清除标记
    if shown["ok"]:
        try:
            os.remove(flag)
        except OSError:
            pass


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # 打包后没有控制台，用弹窗兜底
        try:
            from ctypes import windll
            windll.user32.MessageBoxW(0, str(exc), APP_TITLE + " 启动失败", 0x10)
        except Exception:
            pass
        raise
