"""Rohan-bot shared packages.

`main.py` এখনো একটাই ফাইলে পুরো বট চালায় (repository convention), তাই এই
প্যাকেজগুলোতে শুধু সেই কোড রাখা হয় যেটা আলাদাভাবে import করে unit-test করা সহজ
এবং যেটা বটের বাকি অংশ থেকে স্বাধীন (কোনো Telegram/AI dependency নেই)।
"""

__all__ = ["config", "utils"]
