import os
import re

root_dir = "正文"
vol_dirs = sorted([d for d in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, d)) and d.startswith("0")])

total_chapters = 0
total_chars = 0
errors = []

print("=" * 80)
print("《过度拟合》（OVERFITTING） 全书 8 卷 211 章 正文完整度与字数合规性审计")
print("=" * 80)

for v in vol_dirs:
    v_path = os.path.join(root_dir, v)
    c_files = sorted([f for f in os.listdir(v_path) if f.endswith(".md") and f.startswith("第")])
    vol_chars = 0
    vol_errors = 0
    print(f"\n【{v}】 章节数: {len(c_files)}")
    for f in c_files:
        f_path = os.path.join(v_path, f)
        with open(f_path, "r", encoding="utf-8") as fp:
            content = fp.read()
        cnt = len(re.findall(r'[\u4e00-\u9fa5]', content))
        vol_chars += cnt
        total_chars += cnt
        total_chapters += 1
        
        # Check constraints: 2600 - 3000 chars
        if cnt < 2600 or cnt > 3000:
            vol_errors += 1
            errors.append(f"{v}/{f}: {cnt} 字 (超出 2600-3000 区间)")
            print(f"  [X] {f}: {cnt} 字")
        else:
            pass # print sample if needed
    print(f"  --> 卷总字数: {vol_chars} 汉字 | 合规率: {(len(c_files)-vol_errors)}/{len(c_files)}")

print("\n" + "=" * 80)
print(f"全书总章节数: {total_chapters}")
print(f"全书总字数 (纯汉字): {total_chars} 汉字")
print(f"异常章节数: {len(errors)}")
if errors:
    print("异常列表:")
    for e in errors:
        print("  - " + e)
else:
    print(">>> 恭喜！全书所有章节 100% 符合 2600-3000 字数铁律！<<<")
print("=" * 80)
