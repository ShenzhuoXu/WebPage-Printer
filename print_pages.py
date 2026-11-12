import importlib
from pathlib import Path
import time


try:
    sync_playwright = importlib.import_module("playwright.sync_api").sync_playwright
except ModuleNotFoundError as exc:
    raise ModuleNotFoundError(
        "未找到 Playwright，请先运行：python -m pip install playwright"
    ) from exc

# START_URL = "http://xjtu.zglz.cascorpus.com/main/simplex/text/79fda5f6-fb00-4333-d904-08d9fb38a152"
START_URL = "http://47.99.141.240/main/simplex/text/79fda5f6-fb00-4333-d904-08d9fb38a152"

OUTPUT_DIR = Path("printed_pages")
OUTPUT_DIR.mkdir(exist_ok=True)

MAX_PAGES = 200  # 最大打印页数

def wait_for_changing_chapter() -> bool:
    user_input = input("手动选择需要打印的章节，输入“1”继续，输入“q”退出...")
    if user_input == "1":
        return True
    else:
        return False

#def print_pages_in_chapter():


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False
        )

        page = browser.new_page()

        print("正在打开网页……")
        page.goto(START_URL, wait_until="networkidle", timeout=60000)
        print("已打开页面")

        i = 1
        while wait_for_changing_chapter():

            for j in range(1, MAX_PAGES + 1):
                print(f"正在保存{i}_{j:03d}……")

                page.wait_for_load_state("networkidle")
                # 防止动画/延迟渲染
                time.sleep(5)

                pdf_path = OUTPUT_DIR / f"page_{i}_{j:03d}.pdf"

                page.pdf(
                    path=str(pdf_path),
                    format="A4",
                print_background=True
                )

                print(f"已保存：{pdf_path}")

                next_selectors = [
                    "button.btn-next:not([disabled])",
                    ".el-pagination .btn-next:not([disabled])",
                    ".ant-pagination-next:not(.ant-pagination-disabled)",
                    "button[aria-label='Next Page']",
                    "button[title='Next Page']",
                    "li[title='Next Page']",
                    "button:has-text('>')",
                ]

                clicked = False

                for selector in next_selectors:
                    btn = page.locator(selector).first
                    if btn.count() > 0:
                        # 判断按钮是否为禁用状态
                        btn_class = btn.get_attribute("class") or ""
                        is_disabled = btn.get_attribute("disabled") is not None

                        if "disabled" in btn_class or is_disabled:
                            continue

                        try:
                            btn.click()
                            clicked = True
                            print("进入下一页...")
                            time.sleep(2)
                            break
                        except Exception as e:
                            print(f"点击下一页失败: {e}")
                            pass

                if not clicked:
                    print("未找到有效或未禁用的下一页按钮，任务结束。")
                    break
            i += 1

        browser.close()


if __name__ == "__main__":
    main()