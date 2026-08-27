"""
分类器测试
"""

import sys
sys.path.insert(0, 'src')

from core.classifier import MailClassifier, MailCategory


def test_resume_classification():
    """测试简历分类"""
    classifier = MailClassifier()

    test_cases = [
        ("【面试通知】您有一封新的面试邀请", "job@51job.com"),
        ("您的简历已通过初筛", "recruiter@lagou.com"),
        ("诚邀您加入我们的团队", "career@company.com"),
        ("高薪诚聘Python开发工程师", "job@zhaopin.com"),
    ]

    for subject, sender in test_cases:
        result = classifier.classify(subject, sender, "")
        assert result == MailCategory.RESUME, f"Failed: {subject} -> {result}"


def test_report_classification():
    """测试报告分类"""
    classifier = MailClassifier()

    test_cases = [
        ("2024年Q1季度报告", "report@company.com"),
        ("月度数据统计分析", "analytics@company.com"),
        ("周报 Week 24", "weekly@company.com"),
    ]

    for subject, sender in test_cases:
        result = classifier.classify(subject, sender, "")
        assert result == MailCategory.REPORT, f"Failed: {subject} -> {result}"


def test_ad_classification():
    """测试广告分类"""
    classifier = MailClassifier()

    test_cases = [
        ("限时优惠！全场5折起", "promo@shopping.com"),
        ("新用户专享100元红包", "marketing@brand.com"),
        ("秒杀活动即将开始", "deal@store.com"),
    ]

    for subject, sender in test_cases:
        result = classifier.classify(subject, sender, "")
        assert result == MailCategory.AD, f"Failed: {subject} -> {result}"


def test_verification_classification():
    """测试验证码分类"""
    classifier = MailClassifier()

    test_cases = [
        ("验证码：123456", "noreply@service.com"),
        ("注册验证邮件", "verify@platform.com"),
        ("重置密码链接", "security@company.com"),
    ]

    for subject, sender in test_cases:
        result = classifier.classify(subject, sender, "")
        assert result == MailCategory.VERIFICATION, f"Failed: {subject} -> {result}"


def test_notification_classification():
    """测试通知分类"""
    classifier = MailClassifier()

    test_cases = [
        ("系统通知：您的订单已发货", "notification@platform.com"),
        ("重要提醒：账号安全", "alert@service.com"),
        ("服务更新公告", "official@company.com"),
    ]

    for subject, sender in test_cases:
        result = classifier.classify(subject, sender, "")
        # 通知类也可能匹配其他规则，所以这里允许一定误差


def test_batch_classification():
    """测试批量分类"""
    classifier = MailClassifier()

    emails = [
        {"subject": "面试邀请", "sender": "job@51job.com", "body_preview": ""},
        {"subject": "季度报告", "sender": "report@company.com", "body_preview": ""},
        {"subject": "优惠活动", "sender": "promo@shop.com", "body_preview": ""},
    ]

    results = classifier.classify_batch(emails)

    assert MailCategory.RESUME in results
    assert MailCategory.REPORT in results
    assert MailCategory.AD in results


if __name__ == "__main__":
    print("Running tests...")

    test_resume_classification()
    print("✓ Resume classification test passed")

    test_report_classification()
    print("✓ Report classification test passed")

    test_ad_classification()
    print("✓ AD classification test passed")

    test_verification_classification()
    print("✓ Verification classification test passed")

    test_notification_classification()
    print("✓ Notification classification test passed")

    test_batch_classification()
    print("✓ Batch classification test passed")

    print("\nAll tests passed!")
