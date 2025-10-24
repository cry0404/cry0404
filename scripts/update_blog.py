#!/usr/bin/env python3


import feedparser
import re
import os
import subprocess
import urllib.parse
from datetime import datetime
from typing import List, Dict

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
        # 使用curl命令获取RSS内容，避免SSL问题
        result = subprocess.run(
            ['curl', '-k', '-s', BOOKMARK_RSS_URL],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            print(f"Error fetching bookmark RSS feed: {result.stderr}")
            return []
        
        # 解析RSS内容
        feed = feedparser.parse(result.stdout)
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
    
    # 合并两个部分
    combined_section = blog_section + bookmark_section
    
    # 查找并替换内容部分
    # 使用正则表达式找到博客和书签部分，保留后面的技术栈和统计图表
    content_pattern = r'## Latest Blog Posts.*?(?=## Tech Stack|## GitHub Stats|$)'
    
    if re.search(content_pattern, content, re.DOTALL):
        # 如果存在内容部分，替换它
        new_content = re.sub(content_pattern, combined_section.strip() + '\n\n', content, flags=re.DOTALL)
    else:
        # 如果不存在内容部分，在个人介绍后添加
        intro_pattern = r'(And I have a blog, you can learn more about me from here 👉 \[cry4o4n0tfound\.cn\]\(https://cry4o4n0tfound\.cn\)\.\n\n)'
        if re.search(intro_pattern, content, re.DOTALL):
            new_content = re.sub(intro_pattern, r'\1' + combined_section, content)
        else:
            # 如果找不到合适的位置，在文件末尾添加
            new_content = content + '\n\n' + combined_section
    
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
