"""组装智谱新版 index.html：head_part + 新章节 + 新脚注 + disclaimer + tail"""
import re, os

base = '/Users/panyp/WorkBuddy/宇树科技/底稿/2026-07-21_智谱'
src = os.path.join(base, 'index.html')
t = open(src, encoding='utf-8').read()

# 边界（已通过分析确认）
i1 = t.find('<h2')        # 20199: first chapter
fn_start = 35501          # footnotes div starts
fn_end = 37714            # footnotes div ends
si = t.find('<script')    # 37957: first script tag

head = t[:i1]
disclaimer_section = t[fn_end:si]
tail = t[si:]

# 读取章节片段
parts_dir = os.path.join(base, '_parts')
chapters_html = []
for i in range(1, 10):
    fp = os.path.join(parts_dir, f'ch{i}.html')
    if os.path.exists(fp):
        chapters_html.append(open(fp, encoding='utf-8').read())
    else:
        chapters_html.append(f'<!-- CH{i} MISSING -->')

# 读取脚注
fn_path = os.path.join(parts_dir, 'footnotes.html')
footnotes_html = open(fn_path, encoding='utf-8').read() if os.path.exists(fn_path) else \
    '<div class="footnotes"><h3>注释与来源</h3><ol></ol></div>'

# 组装
new_body = '\n'.join(chapters_html) + '\n' + footnotes_html
new_html = head + new_body + disclaimer_section + tail

out = os.path.join(base, 'index.html')
with open(out, 'w', encoding='utf-8') as f:
    f.write(new_html)
print(f"✅ Assembled: {out} | size={len(new_html)//1024}KB")

# 校验脚注对应
sup_nums = set(re.findall(r'<sup>\[(\d+)\]</sup>', new_html))
li_nums = set(re.findall(r'<li[^>]*>\s*(?:<a[^>]*>)?(?:<span[^>]*>)?', new_html))
# simpler: count <li> in .footnotes ol
fn_count = len(re.findall(r'<li[^>]*>', footnotes_html))
print(f"  <sup>[N] in body: {sup_nums}")
print(f"  <li> in footnotes: {fn_count}")
missing = set(range(1, fn_count+1)) - sup_nums
extra = sup_nums - set(range(1, fn_count+1))
if missing: print(f"  ⚠️ 脚注缺失正文角标: {missing}")
if extra: print(f"  ⚠️ 正文角标无对应脚注: {extra}")
if not missing and not extra:
    print(f"  ✅ 脚注一一对应，OK")
