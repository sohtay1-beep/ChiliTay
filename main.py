import socket
import concurrent.futures
import ipaddress
import time
import flet as ft

def test_tcp_port(ip_str, port=443, timeout=1.5):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        start_time = time.perf_counter()
        result = sock.connect_ex((ip_str, port))
        end_time = time.perf_counter()
        sock.close()
        if result == 0:
            return ip_str, (end_time - start_time) * 1000
    except:
        pass
    return ip_str, None

def main(page: ft.Page):
    page.title = "ChiliTay Premium Builder"
    page.theme_mode = ft.ThemeMode.DARK
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 20

    config_input = ft.TextField(label="لینک کانفیگ اصلی", hint_text="vless://...", border_color="#ff9800", width=400)
    ranges_input = ft.TextField(label="رنج آی‌پي (CIDR)", hint_text="e.g. 66.33.22.0/24", border_color="#ff9800", width=400)
    progress_ring = ft.ProgressRing(visible=False, color="#00ffcc")
    status_text = ft.Text(value="", color="#aaa", text_align=ft.TextAlign.CENTER)
    output_box = ft.TextField(label="کانفیگ‌های اختصاصی ChiliTay", multiline=True, min_lines=6, read_only=True, border_color="#00ffcc", width=400, visible=False)

    def on_copy(e):
        page.set_clipboard(output_box.value)
        page.show_snack_bar(ft.SnackBar(ft.Text("🚀 تمام کانفیگ‌ها کپی شدند!"), open=True))

    copy_button = ft.FilledButton(text="📋 کپی یکجای کانفیگ‌ها", on_click=on_copy, visible=False, width=220)

    def start_process(e):
        output_box.visible = False
        copy_button.visible = False
        progress_ring.visible = True
        status_text.value = "در حال آنالیز کانفیگ..."
        page.update()

        main_config = config_input.value.strip()
        raw_ranges = ranges_input.value.strip()

        if not main_config or not raw_ranges:
            status_text.value = "❌ لطفا تمام کادرها را پر کنید!"
            progress_ring.visible = False
            page.update()
            return

        try:
            prefix, rest = main_config.split("://", 1)
            credentials, connection_details = rest.split("@", 1)
            old_address, after_address = connection_details.split(":", 1)
            port_part = after_address.split("/")[0].split("?")[0].split("#")[0]
            port = int(port_part) if port_part.isdigit() else 443
            params_and_port = after_address.split("#")[0] if "#" in after_address else after_address
        except:
            status_text.value = "❌ فرمت لینک کانفیگ اشتباه است."
            progress_ring.visible = False
            page.update()
            return

        status_text.value = "در حال استخراج آی‌پي‌ها..."
        page.update()
        
        all_ips = []
        for r in raw_ranges.replace(",", " ").split():
            try:
                network = ipaddress.ip_network(r.strip(), strict=False)
                all_ips.extend(list(network.hosts()))
            except:
                continue

        if not all_ips:
            status_text.value = "❌ رنج آی‌پی معتبری یافت نشد."
            progress_ring.visible = False
            page.update()
            return

        status_text.value = f"در حال اسکن {len(all_ips)} آی‌پی روی پورت {port}..."
        page.update()

        healthy_ips = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            results = executor.map(lambda ip: test_tcp_port(str(ip), port=port), all_ips)
            for ip_str, ping_time in results:
                if ping_time is not None:
                    healthy_ips.append((ip_str, ping_time))

        healthy_ips.sort(key=lambda x: x[1])

        if not healthy_ips:
            status_text.value = "❌ هیچ آی‌پی سالمی پیدا نشد."
            progress_ring.visible = False
            page.update()
            return

        generated = []
        for index, (ip, _) in enumerate(healthy_ips[:10], 1):
            generated.append(f"{prefix}://{credentials}@{ip}:{params_and_port}#ChiliTay {index}")

        output_box.value = "\n".join(generated)
        output_box.visible = True
        copy_button.visible = True
        progress_ring.visible = False
        status_text.value = f"تعداد {len(healthy_ips)} آی‌پی تمیز یافت شد. ۱۰تای برتر آماده است!"
        page.update()

    submit_btn = ft.FilledButton(text="⚡ اسکن و ساخت کانفیگ ChiliTay ⚡", width=280, height=50, on_click=start_process)

    page.add(
        ft.Container(height=10),
        ft.Text("🔥 CHILITAY PREMIUM BUILDER 🔥", size=22, weight=ft.FontWeight.BOLD, color="#ff9800"),
        ft.Container(height=10),
        config_input,
        ranges_input,
        ft.Container(height=10),
        submit_btn,
        ft.Container(height=10),
        progress_ring,
        status_text,
        ft.Container(height=10),
        output_box,
        copy_button,
        ft.Container(height=20),
        ft.Text("Powered by ChiliTay Tools v1.0", size=10, color="#444")
    )

if __name__ == "__main__":
    ft.app(target=main)
