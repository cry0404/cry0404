#!/usr/bin/env python3


import feedparser
import re
import urllib.parse
import warnings
from datetime import datetime
from typing import List, Dict

import requests
import urllib3

BLOG_RSS_URL = "https://cry4o4n0tfound.cn/atom.xml"
BOOKMARK_RSS_URL = "https://bookmark.cry4o4n0tfound.cc/feeds/shared"
README_PATH = "README.md"
MAX_POSTS = 5

def fetch_latest_posts() -> List[Dict]:
    """Fetch latest blog posts from RSS feed"""
    try:
        feed = feedparser.parse(BLOG_RSS_URL)
        posts = []
        
        for entry in feed.entries[:MAX_POSTS]:
            # 解析发布日期，优先使用updated字段
            date_parsed = entry.get('updated_parsed') or entry.get('published_parsed')
            if date_parsed:
                date_str = datetime(*date_parsed[:6]).strftime('%Y-%m-%d')
            else:
                date_str = "Unknown"
            
            # 正确编码URL，处理空格等特殊字符
            raw_link = entry.get('link', '#')
            # 只对URL中需要编码的部分进行编码，避免双重编码
            if ' ' in raw_link or any(char in raw_link for char in ['[', ']', '(', ')']):
                encoded_link = urllib.parse.quote(raw_link, safe=':/?#@!$&\'*+,;=')
            else:
                encoded_link = raw_link
            
            posts.append({
                'title': entry.get('title', 'Untitled'),
                'link': encoded_link,
                'date': date_str
            })
        
        return posts
    except Exception as e:
        print(f"Error fetching blog RSS feed: {e}")
        return []

def fetch_latest_bookmarks() -> List[Dict]:
    """Fetch latest bookmarks from RSS feed"""
    try:
        # 禁用 SSL 证书过期警告（书签服务证书已过期但内容可用）
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        response = requests.get(BOOKMARK_RSS_URL, verify=False, timeout=30)
        response.raise_for_status()

        # 解析RSS内容
        feed = feedparser.parse(response.text)
        bookmarks = []
        
        for entry in feed.entries[:MAX_POSTS]:
            # 解析发布日期
            published = entry.get('published_parsed')
            if published:
                date_str = datetime(*published[:6]).strftime('%Y-%m-%d')
            else:
                date_str = "Unknown"
            
            # 正确编码URL，处理空格等特殊字符
            raw_link = entry.get('link', '#')
            # 只对URL中需要编码的部分进行编码，避免双重编码
            if ' ' in raw_link or any(char in raw_link for char in ['[', ']', '(', ')']):
                encoded_link = urllib.parse.quote(raw_link, safe=':/?#@!$&\'*+,;=')
            else:
                encoded_link = raw_link
            
            bookmarks.append({
                'title': entry.get('title', 'Untitled'),
                'link': encoded_link,
                'date': date_str
            })
        
        return bookmarks
    except Exception as e:
        print(f"Error fetching bookmark RSS feed: {e}")
        return []

def update_readme(posts: List[Dict], bookmarks: List[Dict]):
    """Update README.md with latest blog posts and bookmarks"""
    if not posts and not bookmarks:
        print("No posts or bookmarks to update")
        return
    
    # 读取当前 README 内容
    with open(README_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 创建博客部分
    blog_section = ""
    if posts:
        blog_section = "## Latest Blog Posts\n\n"
        blog_section += f"*Auto-updated from [cry4o4n0tfound.cn](https://cry4o4n0tfound.cn)*\n\n"
        
        for post in posts:
            # 清理标题中的特殊字符，避免Markdown解析问题
            clean_title = post['title'].replace('[', '\\[').replace(']', '\\]')
            blog_section += f"- [{clean_title}]({post['link']}) - {post['date']}\n"
        blog_section += "\n"
    
    # 创建书签部分
    bookmark_section = ""
    if bookmarks:
        bookmark_section = "## Recent Bookmarks\n\n"
        bookmark_section += f"*Auto-updated from [bookmark.cry4o4n0tfound.cc](https://bookmark.cry4o4n0tfound.cc)*\n\n"
        
        for bookmark in bookmarks:
            # 清理标题中的特殊字符，避免Markdown解析问题
            clean_title = bookmark['title'].replace('[', '\\[').replace(']', '\\]')
            bookmark_section += f"- [{clean_title}]({bookmark['link']}) - {bookmark['date']}\n"
        bookmark_section += "\n"
    

    
    # 查找并替换内容部分
    # 分别处理博客和书签部分，避免一个失败影响另一个
    blog_pattern = r'## Latest Blog Posts.*?(?=## Recent Bookmarks|## Tech Stack|## GitHub Stats|$)'
    bookmark_pattern = r'## Recent Bookmarks.*?(?=## Tech Stack|## GitHub Stats|$)'
    
    new_content = content
    
    # 更新博客部分
    if posts:
        if re.search(blog_pattern, new_content, re.DOTALL):
            new_content = re.sub(blog_pattern, blog_section.strip() + '\n\n', new_content, flags=re.DOTALL)
        else:
            # 如果不存在博客部分，在个人介绍后添加
            intro_pattern = r'(And I have a blog, you can learn more about me from here 👉 \[cry4o4n0tfound\.cn\]\(https://cry4o4n0tfound\.cn\)\.\n\n)'
            if re.search(intro_pattern, new_content, re.DOTALL):
                new_content = re.sub(intro_pattern, r'\1' + blog_section, new_content)
            else:
                new_content = new_content + '\n\n' + blog_section
    
    # 更新书签部分
    if bookmarks:
        if re.search(bookmark_pattern, new_content, re.DOTALL):
            new_content = re.sub(bookmark_pattern, bookmark_section.strip() + '\n\n', new_content, flags=re.DOTALL)
        else:
            # 如果不存在书签部分，在博客部分后添加
            if posts:
                new_content = new_content.replace(blog_section.strip(), blog_section.strip() + '\n\n' + bookmark_section.strip())
            else:
                new_content = new_content + '\n\n' + bookmark_section
    
    # 写入更新后的内容
    with open(README_PATH, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Updated README with {len(posts)} blog posts and {len(bookmarks)} bookmarks")

def main():
    """Main function"""
    print("Fetching latest blog posts...")
    posts = fetch_latest_posts()
    
    print("Fetching latest bookmarks...")
    bookmarks = fetch_latest_bookmarks()
    
    if posts:
        print(f"Found {len(posts)} blog posts:")
        for post in posts:
            print(f"  - {post['title']} ({post['date']})")
    
    if bookmarks:
        print(f"Found {len(bookmarks)} bookmarks:")
        for bookmark in bookmarks:
            print(f"  - {bookmark['title']} ({bookmark['date']})")
    
    if posts or bookmarks:
        update_readme(posts, bookmarks)
        print("README updated successfully!")
    else:
        print("No posts or bookmarks found or error occurred")

if __name__ == "__main__":
    main()
