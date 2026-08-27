"""
邮件分类助手 - 主界面
LaTeX Paper 论文排版风格
"""

import flet as ft
from flet import (
    Container, Column, Row, Text, TextField, ElevatedButton,
    OutlinedButton, Card, Divider, ProgressBar, Switch,
    icons, colors, padding
)
from typing import Optional, Callable
import asyncio


# LaTeX Paper 风格配色
STYLE = {
    "paper": "#FFFFFF",
    "ink": "#111111",
    "rule_gray": "#D4D4D0",
    "muted": "#6B6B66",
    "theorem_fill": "#F5F5F0",
    "hyperref_blue": "#0B5394",
    "accent": "#333333",
}


class LaTeXTheme:
    """LaTeX Paper 主题"""

    @staticmethod
    def paper_container(content=None, padding_val=20):
        """纸张容器"""
        return Container(
            content=content,
            bgcolor=STYLE["paper"],
            padding=padding_val,
            border=ft.border.all(1, STYLE["rule_gray"]),
        )

    @staticmethod
    def theorem_card(title: str, content, subtitle: str = ""):
        """定理风格卡片（用于统计卡片）"""
        return Container(
            content=Column([
                Text(title, size=12, weight=ft.FontWeight.W_600, color=STYLE["ink"]),
                Text(subtitle, size=10, color=STYLE["muted"]),
                content,
            ], spacing=8),
            bgcolor=STYLE["theorem_fill"],
            border=ft.border.only(left=ft.border.BorderSide(2, STYLE["ink"])),
            padding=15,
        )

    @staticmethod
    def section_header(number: str, title: str):
        """章节标题（带编号）"""
        return Container(
            content=Row([
                Text(f"{number}", weight=ft.FontWeight.W_700, color=STYLE["ink"]),
                Text(" ", size=14),
                Text(title, weight=ft.FontWeight.W_600, color=STYLE["ink"]),
            ]),
            padding=ft.padding.only(bottom=10, top=5),
        )

    @staticmethod
    def primary_button(text: str, icon: Optional[str] = None, on_click=None, disabled=False):
        """主要按钮（墨黑实底）"""
        return ElevatedButton(
            content=Row([
                Text(icon, size=16) if icon else Text(""),
                Text(f" {text}", weight=ft.FontWeight.W_600),
            ] if icon else [Text(text, weight=ft.FontWeight.W_600)]),
            on_click=on_click,
            disabled=disabled,
            style=ft.ButtonStyle(
                bgcolor=STYLE["ink"],
                color=STYLE["paper"],
                shape=ft.RoundedRectangleBorder(radius=0),
                padding=ft.padding.symmetric(horizontal=20, vertical=12),
            ),
        )

    @staticmethod
    def secondary_button(text: str, icon: Optional[str] = None, on_click=None):
        """次要按钮（细边框）"""
        return OutlinedButton(
            content=Row([
                Text(icon, size=16) if icon else Text(""),
                Text(f" {text}", weight=ft.FontWeight.W_500),
            ] if icon else [Text(text, weight=ft.FontWeight.W_500)]),
            on_click=on_click,
            style=ft.ButtonStyle(
                color=STYLE["ink"],
                side=ft.BorderSide(1, STYLE["ink"]),
                shape=ft.RoundedRectangleBorder(radius=0),
                padding=ft.padding.symmetric(horizontal=20, vertical=12),
            ),
        )

    @staticmethod
    def input_field(
        label: str,
        value: str = "",
        password: bool = False,
        on_change: Optional[Callable] = None,
        hint: str = "",
    ):
        """输入框"""
        return Column([
            Text(label, size=12, weight=ft.FontWeight.W_600, color=STYLE["ink"]),
            TextField(
                value=value,
                password=password,
                hint_text=hint,
                on_change=on_change,
                border_color=STYLE["rule_gray"],
                focused_border_color=STYLE["ink"],
                border_radius=0,
                text_style=ft.TextStyle(color=STYLE["ink"]),
                hint_style=ft.TextStyle(color=STYLE["muted"]),
            ),
        ], spacing=4)

    @staticmethod
    def link_text(text: str, on_click: Optional[Callable] = None):
        """链接文本（hyperref蓝）"""
        return Text(
            text,
            color=STYLE["hyperref_blue"],
            size=12,
            on_click=on_click,
            style=ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE),
        )


class DocumentHead:
    """文档头部"""

    @staticmethod
    def build(title: str, subtitle: str = "", version: str = ""):
        """构建文档头部"""
        children = [
            Text(title, size=32, weight=ft.FontWeight.W_700, color=STYLE["ink"]),
        ]
        if subtitle:
            children.append(Text(subtitle, size=12, color=STYLE["muted"]))
        if version:
            children.append(Text(f"v{version}", size=10, color=STYLE["muted"], italic=True))

        return Container(
            content=Column(children, spacing=4, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.symmetric(vertical=30),
            alignment=ft.alignment.center,
        )


class MainApp:
    """主应用"""

    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "邮件分类助手"
        self.page.theme_mode = ft.ThemeMode.LIGHT

        # 状态变量
        self.email_input = ""
        self.auth_code_input = ""
        self.is_connected = False
        self.is_classifying = False
        self.classification_results = {}
        self.status_message = ""

        # 回调
        self.on_connect_callback: Optional[Callable] = None
        self.on_classify_callback: Optional[Callable] = None
        self.on_disconnect_callback: Optional[Callable] = None

        self._init_ui()

    def _init_ui(self):
        """初始化UI"""
        # 页面布局
        self.page.add(
            # 文档头部
            DocumentHead.build(
                title="邮件分类助手",
                subtitle="基于规则的智能邮件分类系统",
                version="1.0.0"
            ),
            Divider(color=STYLE["ink"], thickness=2),
        )

        # 标签页
        self.tabs = ft.Tabs(
            selected_index=0,
            tabs=[
                ft.Tab(
                    text="1  配置",
                    content=self._build_config_tab(),
                ),
                ft.Tab(
                    text="2  分类",
                    content=self._build_classify_tab(),
                ),
                ft.Tab(
                    text="3  历史",
                    content=self._build_history_tab(),
                ),
            ],
            divider_color=STYLE["rule_gray"],
            indicator_color=STYLE["ink"],
            label_color=STYLE["muted"],
            selected_label_color=STYLE["ink"],
        )
        self.page.add(self.tabs)

        # 状态栏
        self.status_bar = Container(
            content=Row([
                Text("状态: ", size=11, color=STYLE["muted"]),
                Text("未连接", size=11, color=STYLE["muted"], ref=self.page),
            ]),
            padding=ft.padding.symmetric(vertical=10),
        )
        self.page.add(self.status_bar)

    def _build_config_tab(self):
        """配置标签页"""
        return Container(
            content=Column([
                # 1.1 连接配置
                LaTeXTheme.section_header("1.1", "连接配置"),
                LaTeXTheme.paper_container(
                    Column([
                        LaTeXTheme.input_field(
                            label="邮箱地址",
                            hint="your_email@qq.com",
                            on_change=lambda e: setattr(self, 'email_input', e.control.value),
                        ),
                        LaTeXTheme.input_field(
                            label="授权码",
                            hint="QQ邮箱授权码（非密码）",
                            password=True,
                            on_change=lambda e: setattr(self, 'auth_code_input', e.control.value),
                        ),
                        Row([
                            LaTeXTheme.primary_button("连接", "📡", self._handle_connect),
                            LaTeXTheme.secondary_button("断开", "✋", self._handle_disconnect),
                        ], spacing=12),
                    ], spacing=16),
                ),

                ft.Container(height=20),

                # 1.2 文件夹配置
                LaTeXTheme.section_header("1.2", "文件夹映射"),
                LaTeXTheme.paper_container(
                    Column([
                        self._build_folder_mapping_row("简历类", "简历分类"),
                        self._build_folder_mapping_row("报告类", "报告分类"),
                        self._build_folder_mapping_row("广告类", "广告分类"),
                        self._build_folder_mapping_row("通知类", "通知分类"),
                        self._build_folder_mapping_row("验证码类", "验证码分类"),
                    ], spacing=12),
                ),

                ft.Container(height=20),

                # 1.3 帮助
                LaTeXTheme.section_header("1.3", "获取授权码"),
                LaTeXTheme.paper_container(
                    Column([
                        Text("1. 登录 QQ 邮箱", size=11, color=STYLE["ink"]),
                        Text("2. 进入设置 → 账户", size=11, color=STYLE["ink"]),
                        Text("3. 开启 IMAP/SMTP 服务", size=11, color=STYLE["ink"]),
                        Text("4. 生成授权码并妥善保存", size=11, color=STYLE["ink"]),
                    ], spacing=4),
                ),
            ], spacing=0, scroll=ft.ScrollMode.AUTO),
            padding=20,
        )

    def _build_folder_mapping_row(self, category: str, default_folder: str):
        """构建文件夹映射行"""
        return Row([
            Text(category, size=12, weight=ft.FontWeight.W_500, width=80),
            TextField(
                value=default_folder,
                border_color=STYLE["rule_gray"],
                focused_border_color=STYLE["ink"],
                border_radius=0,
                text_style=ft.TextStyle(color=STYLE["ink"], size=11),
                width=200,
            ),
            Switch(value=True, active_color=STYLE["ink"]),
            Text("启用", size=10, color=STYLE["muted"]),
        ], spacing=12)

    def _build_classify_tab(self):
        """分类标签页"""
        return Container(
            content=Column([
                # 2.1 分类控制
                LaTeXTheme.section_header("2.1", "执行分类"),
                Row([
                    LaTeXTheme.primary_button("开始分类", "▶", self._handle_classify, disabled=False),
                    Text("每次最多处理 100 封邮件", size=11, color=STYLE["muted"]),
                ], spacing=12),

                ft.Container(height=15),

                # 进度条
                self.progress_bar := ProgressBar(
                    value=0,
                    color=STYLE["ink"],
                    bgcolor=STYLE["rule_gray"],
                    height=4,
                    visible=False,
                ),

                ft.Container(height=20),

                # 2.2 分类结果
                LaTeXTheme.section_header("2.2", "分类统计"),
                self.results_container := Column([], spacing=12, visible=False),

                ft.Container(height=20),

                # 2.3 详细列表
                LaTeXTheme.section_header("2.3", "邮件列表"),
                self.email_list_container := Container(
                    content=Text("暂无数据", size=11, color=STYLE["muted"]),
                    visible=False,
                ),
            ], spacing=0, scroll=ft.ScrollMode.AUTO),
            padding=20,
        )

    def _build_history_tab(self):
        """历史记录标签页"""
        return Container(
            content=Column([
                LaTeXTheme.section_header("3", "分类历史"),
                LaTeXTheme.paper_container(
                    Column([
                        Text("暂无历史记录", size=12, color=STYLE["muted"]),
                        Text("分类历史将在首次分类后显示", size=11, color=STYLE["muted"]),
                    ], spacing=8),
                ),
            ], spacing=0, scroll=ft.ScrollMode.AUTO),
            padding=20,
        )

    def _handle_connect(self, e):
        """处理连接"""
        if self.on_connect_callback:
            asyncio.create_task(self._connect_async())

    async def _connect_async(self):
        """异步连接"""
        self.status_message = "正在连接..."
        self.update_status()
        self.progress_bar.visible = True

        if self.on_connect_callback:
            success = await self.on_connect_callback(self.email_input, self.auth_code_input)
            if success:
                self.is_connected = True
                self.status_message = "连接成功"
            else:
                self.status_message = "连接失败，请检查凭据"
                self.is_connected = False

        self.progress_bar.visible = False
        self.update_status()

    def _handle_disconnect(self, e):
        """处理断开"""
        if self.on_disconnect_callback:
            self.on_disconnect_callback()
        self.is_connected = False
        self.status_message = "已断开"
        self.update_status()

    def _handle_classify(self, e):
        """处理分类"""
        if self.is_classifying:
            return
        self.is_classifying = True

        if self.on_classify_callback:
            asyncio.create_task(self._classify_async())

    async def _classify_async(self):
        """异步分类"""
        self.progress_bar.visible = True
        self.progress_bar.value = 0.1
        self.status_message = "正在拉取邮件..."
        self.update_status()

        if self.on_classify_callback:
            results = await self.on_classify_callback()
            self.classification_results = results
            self.display_results(results)

        self.progress_bar.value = 1.0
        self.progress_bar.visible = False
        self.is_classifying = False
        self.status_message = "分类完成"
        self.update_status()

    def display_results(self, results: dict):
        """显示分类结果"""
        self.results_container.visible = True
        self.email_list_container.visible = True

        # 清空并重新构建
        self.results_container.controls.clear()

        for category, emails in results.items():
            if not emails:
                continue

            category_name = category.value[0] if hasattr(category, 'value') else str(category)
            emoji = category.value[1] if hasattr(category, 'value') else ""

            self.results_container.controls.append(
                LaTeXTheme.theorem_card(
                    title=f"{emoji} {category_name}",
                    subtitle=f"{len(emails)} 封邮件",
                    content=Column([
                        LaTeXTheme.secondary_button(
                            f"查看详情 ({len(emails)})",
                            on_click=lambda e, c=category: self._show_category_detail(c)
                        ),
                    ], spacing=8),
                )
            )

        self.results_container.update()

    def _show_category_detail(self, category):
        """显示分类详情"""
        emails = self.classification_results.get(category, [])
        self.email_list_container.content = Column([
            Text(f"{category.value[0]} - {len(emails)} 封邮件", size=14, weight=ft.FontWeight.W_600),
            Divider(color=STYLE["rule_gray"]),
            *[self._build_email_item(email) for email in emails[:20]],  # 最多显示20条
            Text(f"... 共 {len(emails)} 封" if len(emails) > 20 else "", size=11, color=STYLE["muted"]),
        ], spacing=8)
        self.email_list_container.visible = True
        self.email_list_container.update()

    def _build_email_item(self, email: dict):
        """构建邮件项"""
        return Container(
            content=Column([
                Text(email.get("subject", "无主题"), size=12, weight=ft.FontWeight.W_500),
                Text(f"发件人: {email.get('sender', '未知')}", size=10, color=STYLE["muted"]),
            ], spacing=2),
            border=ft.border.only(bottom=ft.border.BorderSide(1, STYLE["rule_gray"])),
            padding=8,
        )

    def update_status(self):
        """更新状态栏"""
        self.page.controls[-1].content.controls[1].value = self.status_message
        self.page.update()


def main(page: ft.Page):
    """主入口"""
    app = MainApp(page)
    page.window_width = 800
    page.window_height = 700
    page.window_resizable = True


if __name__ == "__main__":
    ft.app(target=main)
