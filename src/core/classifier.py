"""
邮件分类引擎
基于关键词和发件人特征进行邮件分类
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class MailCategory(Enum):
    """邮件分类枚举"""
    RESUME = ("简历类", "📄")
    REPORT = ("报告类", "📊")
    AD = ("广告类", "📢")
    NOTIFICATION = ("通知类", "🔔")
    VERIFICATION = ("验证码类", "🔐")
    UNKNOWN = ("未分类", "❓")


@dataclass
class ClassificationRule:
    """分类规则"""
    category: MailCategory
    keywords: List[str]
    sender_patterns: List[str]
    priority: int = 1


class MailClassifier:
    """邮件分类器"""

    # 默认分类规则
    DEFAULT_RULES = [
        # 简历类
        ClassificationRule(
            category=MailCategory.RESUME,
            keywords=["简历", "求职", "应聘", "offer", "面试", "加入我们", "招聘", "岗位", "薪水", "薪资"],
            sender_patterns=["job", "zhaopin", "career", "talent", "51job", "lagou", "boss", "zhipin", "liepin"],
            priority=3
        ),
        # 报告类
        ClassificationRule(
            category=MailCategory.REPORT,
            keywords=["报告", "分析", "报表", "月报", "周报", "年报", "季度", "统计", "数据报告", "总结"],
            sender_patterns=["report", "analytics", "bi", "dashboard"],
            priority=2
        ),
        # 验证码类
        ClassificationRule(
            category=MailCategory.VERIFICATION,
            keywords=["验证码", "注册", "登录", "token", "密码", "重置", "verify", "activation", "激活", "安全"],
            sender_patterns=["no-reply", "noreply", "security", "alert", "notification"],
            priority=4
        ),
        # 广告类
        ClassificationRule(
            category=MailCategory.AD,
            keywords=["促销", "优惠", "折扣", "限时", "秒杀", "满减", "红包", "抽奖", "免费", "新品", "推荐"],
            sender_patterns=["marketing", "promotion", "sale", "deal", "coupon", "newsletter"],
            priority=1
        ),
        # 通知类
        ClassificationRule(
            category=MailCategory.NOTIFICATION,
            keywords=["通知", "提醒", "公告", "系统消息", "重要", "提醒您", "请注意", "关于", "更新", "订单"],
            sender_patterns=["official", "support", "service", "help", "notification"],
            priority=3
        ),
    ]

    def __init__(self, custom_rules: Optional[List[ClassificationRule]] = None):
        """
        初始化分类器

        Args:
            custom_rules: 自定义规则，None则使用默认规则
        """
        self.rules = custom_rules if custom_rules else self.DEFAULT_RULES
        # 按优先级排序（高优先级先匹配）
        self.rules.sort(key=lambda x: x.priority, reverse=True)

    def classify(self, subject: str, sender: str, body_preview: str = "") -> MailCategory:
        """
        分类单封邮件

        Args:
            subject: 邮件主题
            sender: 发件人地址
            body_preview: 邮件正文预览

        Returns:
            邮件分类
        """
        text = f"{subject} {body_preview}".lower()
        sender_lower = sender.lower()

        for rule in self.rules:
            # 检查关键词匹配
            keyword_match = any(kw.lower() in text for kw in rule.keywords)
            # 检查发件人模式匹配
            sender_match = any(pattern.lower() in sender_lower for pattern in rule.sender_patterns)

            # 双重匹配
            if keyword_match and sender_match:
                return rule.category

            # 高优先级规则：关键词强匹配
            if keyword_match:
                matched_count = sum(1 for kw in rule.keywords if kw.lower() in text)
                # 多个关键词匹配 或 高优先级规则
                if matched_count >= 2 or rule.priority >= 3:
                    return rule.category

        return MailCategory.UNKNOWN

    def classify_batch(self, emails: List[dict]) -> dict:
        """
        批量分类邮件

        Args:
            emails: 邮件列表，每项包含 subject, sender, body_preview

        Returns:
            分类结果字典 {category: [emails]}
        """
        results = {cat: [] for cat in MailCategory}
        results.pop(MailCategory.UNKNOWN, None)  # 移除UNKNOWN作为键

        for email in emails:
            category = self.classify(
                subject=email.get("subject", ""),
                sender=email.get("sender", ""),
                body_preview=email.get("body_preview", "")
            )
            if category != MailCategory.UNKNOWN:
                results[category].append(email)
            else:
                # 将未分类邮件归入UNKNOWN
                if MailCategory.UNKNOWN not in results:
                    results[MailCategory.UNKNOWN] = []
                results[MailCategory.UNKNOWN].append(email)

        return results
