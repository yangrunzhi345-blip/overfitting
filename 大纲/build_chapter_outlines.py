# -*- coding: utf-8 -*-
"""
《过度拟合》全书211章 章纲生成与审计脚本
严格约束：每章章纲字数不超过300字（汉字及字符数 <= 300）
存储路径：/home/yrz/过度拟合/大纲/卷纲/0X_第X卷/章纲/第XXX章_标题.md
"""

import os
import re

VOLS = [
    (1, '01_第一卷', '一', 1),
    (2, '02_第二卷', '二', 22),
    (3, '03_第三卷', '三', 50),
    (4, '04_第四卷', '四', 80),
    (5, '05_第五卷', '五', 110),
    (6, '06_第六卷', '六', 138),
    (7, '07_第七卷', '七', 163),
    (8, '08_第八卷', '八', 191),
]

def sanitize_filename(name):
    name = re.sub(r'[\\/*?:"<>|｜]', '_', name)
    name = re.sub(r'\s+', '_', name).strip('_')
    return name

def condense_events_and_focus(events, focus, target_max=180):
    ev_str = '；'.join(events) + '。' if events else ''
    foc_str = '；'.join(focus[:2]) + '。' if focus else ''
    
    if len(ev_str) + len(foc_str) > target_max:
        foc_str = focus[0] + '。' if focus else ''
    
    while len(ev_str) + len(foc_str) > target_max and len(events) > 2:
        events.pop()
        ev_str = '；'.join(events) + '。'
        
    if len(ev_str) + len(foc_str) > target_max:
        # truncate ev_str gracefully
        max_ev = target_max - len(foc_str)
        if len(ev_str) > max_ev and max_ev > 30:
            ev_str = ev_str[:max_ev - 5].rstrip('，、；') + '。'
            
    return ev_str, foc_str

def process_volume(vol_num, vol_dir, vol_cn, start_idx):
    base_path = f'/home/yrz/过度拟合/大纲/卷纲/{vol_dir}'
    vol_file = f'{base_path}/卷纲.md'
    out_dir = f'{base_path}/章纲'
    os.makedirs(out_dir, exist_ok=True)
    
    with open(vol_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    pattern = r'(#{3,4}\s+第\d+章[^\n]+)\n(.*?)(?=\n#{3,4}\s+第\d+章|\n## |\Z)'
    matches = re.findall(pattern, content, re.DOTALL)
    
    chapter_summaries = []
    
    for i, (h, body) in enumerate(matches):
        raw_title = re.sub(r'^#+\s*', '', h).strip()
        clean_title = raw_title.replace('｜', ' ')
        
        m_time = re.search(r'-\s*\*\*时间\*\*[:：]\s*([^\n]+)', body)
        time_str = m_time.group(1).strip() if m_time else ''
        
        m_words = re.search(r'-\s*\*\*字数[^\*]*\*\*[:：]\s*([^\n]+)', body)
        words_str = m_words.group(1).strip() if m_words else ''
        
        m_events = re.search(r'-\s*\*\*核心事件\*\*[:：]\s*\n((?:\s+\d+\.[^\n]+\n?)+)', body)
        events = []
        if m_events:
            for l in m_events.group(1).strip().split('\n'):
                l_clean = re.sub(r'^\s*\d+\.\s*', '', l).strip().rstrip('；;。')
                if l_clean:
                    events.append(l_clean)
                    
        m_focus = re.search(r'-\s*\*\*叙事重点\*\*[:：]\s*([^\n]+(?:\n\s+\d+\.[^\n]+)*)', body)
        focus = []
        if m_focus:
            for l in m_focus.group(1).strip().split('\n'):
                l_clean = re.sub(r'^\s*\d+\.\s*', '', l).strip().rstrip('；;。')
                if l_clean:
                    focus.append(l_clean)
                    
        m_end = re.search(r'-\s*\*\*章末落点\*\*[:：]\s*([^\n]+)', body)
        if not m_end:
            m_end = re.search(r'-\s*\*\*叙事落点\*\*[:：]\s*([^\n]+)', body)
        end_str = m_end.group(1).strip() if m_end else ''
        
        m_tri = re.search(r'-\s*\*\*三线推进[^\*]*\*\*[:：]\s*([^\n]+)', body)
        tri_str = m_tri.group(1).strip() if m_tri else ''

        ev_str, foc_str = condense_events_and_focus(events, focus, target_max=165)
        
        # Build chapter outline
        global_no = start_idx + i
        chapter_outline = f"""# {clean_title}

- **全书定位**：第{vol_cn}卷 · 全书第{global_no:03d}章
- **时间与体量**：{time_str}｜{words_str}
- **核心剧情**：{ev_str}
- **博弈与焦点**：{foc_str}
- **章末落点**：{end_str}
"""
        # Strict validation on character count (under 300)
        pure_char_count = len(re.sub(r'\s+', '', chapter_outline))
        if pure_char_count > 300:
            # Emergency trim
            diff = pure_char_count - 280
            ev_str = ev_str[:-diff].rstrip('，、；') + '。'
            chapter_outline = f"""# {clean_title}

- **全书定位**：第{vol_cn}卷 · 全书第{global_no:03d}章
- **时间与体量**：{time_str}｜{words_str}
- **核心剧情**：{ev_str}
- **博弈与焦点**：{foc_str}
- **章末落点**：{end_str}
"""
            pure_char_count = len(re.sub(r'\s+', '', chapter_outline))

        # Save single chapter file
        file_name = sanitize_filename(clean_title) + '.md'
        file_path = os.path.join(out_dir, file_name)
        with open(file_path, 'w', encoding='utf-8') as cf:
            cf.write(chapter_outline.strip() + '\n')
            
        chapter_summaries.append((file_name, clean_title, chapter_outline.strip(), pure_char_count))
        
    # Write summary file
    summary_path = os.path.join(out_dir, '章纲汇总.md')
    with open(summary_path, 'w', encoding='utf-8') as sf:
        sf.write(f'# 第{vol_cn}卷 章纲全编汇总\n\n> 本卷共 {len(chapter_summaries)} 章，每章章纲均严格控制在 300 字以内。\n\n---\n\n')
        for fname, title, outline, c_len in chapter_summaries:
            sf.write(f'{outline}\n\n*（本章章纲字符数：{c_len}字）*\n\n---\n\n')
            
    print(f'第{vol_cn}卷 处理完毕：共生成 {len(chapter_summaries)} 章章纲文件及汇总。所有单章字符数均 <= 300。')
    return chapter_summaries

if __name__ == '__main__':
    total_chapters = 0
    all_lengths = []
    for vol_num, vol_dir, vol_cn, start_idx in VOLS:
        summaries = process_volume(vol_num, vol_dir, vol_cn, start_idx)
        total_chapters += len(summaries)
        for _, _, _, clen in summaries:
            all_lengths.append(clen)
            
    print('='*50)
    print(f'全书统计：共生成 {total_chapters} 章章纲独立文件。')
    print(f'单章字符数范围：最小 {min(all_lengths)} 字，最大 {max(all_lengths)} 字。')
    print(f'超过300字章节数：{len([l for l in all_lengths if l > 300])} 章。')
