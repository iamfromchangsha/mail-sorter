"""
QQ邮箱 IMAP 客户端
处理邮件连接、拉取和文件夹操作
"""

import imaplib
import email
from email.header import decode_header
from dataclasses import dataclass
from typing import List, Optional, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Mail:
    """邮件数据结构"""
    uid: str
    subject: str
    sender: str
    sender_name: str
    date: str
    body_preview: str
    is_read: bool
    folder: str


class QQMailClient:
    """QQ邮箱 IMAP 客户端"""

    IMAP_SERVER = "imap.qq.com"
    IMAP_PORT = 993

    def __init__(self, email_addr: str, auth_code: str):
        """
        初始化客户端

        Args:
            email_addr: QQ邮箱地址
            auth_code: QQ邮箱授权码（非密码）
        """
        self.email_addr = email_addr
        self.auth_code = auth_code
        self.conn: Optional[imaplib.IMAP4_SSL] = None

    def connect(self) -> bool:
        """
        建立IMAP连接

        Returns:
            连接是否成功
        """
        try:
            self.conn = imaplib.IMAP4_SSL(self.IMAP_SERVER, self.IMAP_PORT)
            self.conn.login(self.email_addr, self.auth_code)
            logger.info(f"成功连接到 {self.email_addr}")
            return True
        except imaplib.IMAP4.error as e:
            logger.error(f"IMAP连接失败: {e}")
            return False

    def disconnect(self):
        """关闭连接"""
        if self.conn:
            try:
                self.conn.logout()
                logger.info("已断开连接")
            except Exception:
                pass

    def _decode_email_header(self, header: str) -> str:
        """解码邮件头"""
        if not header:
            return ""
        decoded_parts = decode_header(header)
        result = []
        for part, charset in decoded_parts:
            if isinstance(part, bytes):
                charset = charset or 'utf-8'
                try:
                    result.append(part.decode(charset, errors='replace'))
                except (LookupError, UnicodeDecodeError):
                    result.append(part.decode('utf-8', errors='replace'))
            else:
                result.append(part)
        return ''.join(result)

    def _parse_email_address(self, sender: str) -> Tuple[str, str]:
        """解析发件人地址，返回 (显示名, 邮箱地址)"""
        if not sender:
            return "", ""
        try:
            msg = email.message_from_string(f"From: {sender}")
            from_addr = msg.get('From', '')
            name, addr = email.utils.parseaddr(from_addr)
            return name or addr, addr
        except Exception:
            return sender, sender

    def _get_body_preview(self, msg) -> str:
        """获取邮件正文预览"""
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    try:
                        payload = part.get_payload(decode=True)
                        charset = part.get_content_charset() or 'utf-8'
                        body = payload.decode(charset, errors='replace')
                        break
                    except Exception:
                        continue
        else:
            try:
                payload = msg.get_payload(decode=True)
                charset = msg.get_content_charset() or 'utf-8'
                body = payload.decode(charset, errors='replace')
            except Exception:
                pass
        return body[:500].replace('\n', ' ').replace('\r', '')

    def fetch_emails(self, folder: str = "INBOX", limit: int = 100) -> List[Mail]:
        """
        拉取邮件列表

        Args:
            folder: 文件夹名称，默认收件箱
            limit: 最大数量

        Returns:
            邮件列表
        """
        if not self.conn:
            if not self.connect():
                return []

        try:
            # 选择文件夹
            status, _ = self.conn.select(folder)
            if status != 'OK':
                logger.error(f"无法选择文件夹: {folder}")
                return []

            # 搜索所有邮件
            status, messages = self.conn.search(None, 'ALL')
            if status != 'OK':
                return []

            mail_ids = messages[0].split()
            if not mail_ids:
                return []

            # 取最新的邮件
            mail_ids = mail_ids[-limit:]
            mails = []

            for mail_id in mail_ids:
                try:
                    status, msg_data = self.conn.fetch(mail_id, '(RFC822)')
                    if status != 'OK':
                        continue

                    raw_email = msg_data[0][1]
                    msg = email.message_from_bytes(raw_email)

                    # 解析邮件信息
                    subject = self._decode_email_header(msg.get('Subject', ''))
                    raw_sender = msg.get('From', '')
                    sender_name, sender_addr = self._parse_email_address(raw_sender)
                    date = msg.get('Date', '')
                    is_read = 'Seen' in msg.get('Flags', '')

                    # 获取UID
                    status, uid_data = self.conn.fetch(mail_id, '(UID)')
                    uid = mail_id.decode() if isinstance(mail_id, bytes) else mail_id

                    mail = Mail(
                        uid=uid,
                        subject=subject,
                        sender=sender_addr,
                        sender_name=sender_name,
                        date=date,
                        body_preview=self._get_body_preview(msg),
                        is_read=is_read,
                        folder=folder
                    )
                    mails.append(mail)
                except Exception as e:
                    logger.warning(f"解析邮件失败: {e}")
                    continue

            logger.info(f"成功拉取 {len(mails)} 封邮件")
            return mails

        except imaplib.IMAP4.error as e:
            logger.error(f"拉取邮件失败: {e}")
            return []

    def move_email(self, mail_uid: str, source_folder: str, target_folder: str) -> bool:
        """
        移动邮件到目标文件夹

        Args:
            mail_uid: 邮件UID
            source_folder: 源文件夹
            target_folder: 目标文件夹

        Returns:
            是否成功
        """
        if not self.conn:
            return False

        try:
            # 选择源文件夹
            self.conn.select(source_folder)

            # 使用 COPY 命令复制邮件
            status, _ = self.conn.copy(mail_uid, target_folder)
            if status != 'OK':
                logger.error(f"复制邮件失败: {mail_uid}")
                return False

            # 删除原邮件
            self.conn.store(mail_uid, '+FLAGS', '\\Deleted')
            self.conn.expunge()

            logger.info(f"邮件 {mail_uid} 已移动到 {target_folder}")
            return True

        except imaplib.IMAP4.error as e:
            logger.error(f"移动邮件失败: {e}")
            return False

    def create_folder(self, folder_name: str) -> bool:
        """
        创建文件夹

        Args:
            folder_name: 文件夹名称

        Returns:
            是否成功
        """
        if not self.conn:
            return False

        try:
            # 使用 CREATE 命令创建文件夹
            status, _ = self.conn.create(folder_name)
            if status == 'OK':
                logger.info(f"文件夹 {folder_name} 创建成功")
                return True
            else:
                logger.warning(f"文件夹 {folder_name} 可能已存在")
                return True  # 已存在也视为成功
        except imaplib.IMAP4.error as e:
            logger.error(f"创建文件夹失败: {e}")
            return False

    def list_folders(self) -> List[str]:
        """
        列出所有文件夹

        Returns:
            文件夹名称列表
        """
        if not self.conn:
            return []

        try:
            status, folders = self.conn.list()
            if status != 'OK':
                return []

            folder_list = []
            for folder in folders:
                if isinstance(folder, bytes):
                    folder = folder.decode('utf-8', errors='replace')
                # 提取文件夹名称
                parts = folder.split('"."')
                if len(parts) > 1:
                    folder_name = parts[-1].strip().strip('"')
                    folder_list.append(folder_name)

            return folder_list
        except Exception as e:
            logger.error(f"列出文件夹失败: {e}")
            return []

    def mark_as_read(self, mail_uid: str, folder: str) -> bool:
        """标记邮件为已读"""
        if not self.conn:
            return False

        try:
            self.conn.select(folder)
            self.conn.store(mail_uid, '+FLAGS', '\\Seen')
            return True
        except Exception as e:
            logger.error(f"标记已读失败: {e}")
            return False

    def mark_as_unread(self, mail_uid: str, folder: str) -> bool:
        """标记邮件为未读"""
        if not self.conn:
            return False

        try:
            self.conn.select(folder)
            self.conn.store(mail_uid, '-FLAGS', '\\Seen')
            return True
        except Exception as e:
            logger.error(f"标记未读失败: {e}")
            return False
