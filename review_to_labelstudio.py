"""Paste a WB table row and save one Label Studio task. Standard library only."""
import csv
import json
import re
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

SOURCE = 'https://huggingface.co/datasets/Hplss/wb-review-dataset'


def convert(raw):
    lines = [s.strip() for s in raw.strip().splitlines() if s.strip()]
    rows = []
    for line in lines:
        if re.fullmatch(r'[|\s:\-]+', line):
            continue
        if '\t' in line:
            row = next(csv.reader([line], delimiter='\t'))
        elif '|' in line:
            row = line.strip('|').split('|')
        else:
            continue
        row = [v.strip() for v in row]
        if row and re.fullmatch(r'[\d,\s\u00a0]+', row[0]):
            rows.append(row)
    if not rows and len(lines) in (7, 8) and re.fullmatch(r'[\d,\s\u00a0]+', lines[0]):
        rows = [lines]
    if len(rows) != 1:
        raise ValueError('Вставьте одну строку таблицы: ID отзыва, ID товара, категория, оценка, text, pros, cons. Можно с Markdown-заголовком.')
    row = rows[0]
    if len(row) == 8:
        review_id, product_id, category, category_label, rating, text, pros, cons = row
    elif len(row) == 7:
        review_id, product_id, category_label, rating, text, pros, cons = row
    else:
        raise ValueError(f'Получено {len(row)} столбцов; ожидается 7 или 8. Копируйте строку целиком. Символ | внутри текста при Markdown-вставке не поддерживается.')
    def identifier(value):
        return int(re.sub(r'[,\s\u00a0]', '', value))
    def content(value):
        return '' if value.strip().lower() in ('null', 'none', 'nan', '') else value.strip()
    sections = []
    for title, value in [('Отзыв', text), ('Достоинства', pros), ('Недостатки', cons)]:
        if content(value):
            sections.append(f'{title}:\n{content(value)}')
    if not sections:
        raise ValueError('В отзыве нет текста, достоинств или недостатков.')
    return {'data': {
        'text': '\n\n'.join(sections),
        'source_review_id': identifier(review_id),
        'source_product_id': identifier(product_id),
        'category_label': category_label,
        'source_url': SOURCE,
        'access_date': datetime.now().date().isoformat(),
        'license': 'CC-BY-NC-SA-4.0',
    }}


def main():
    window = tk.Tk()
    window.title('WB → Label Studio')
    window.geometry('850x620')
    tk.Label(window, text='Вставь строку WB: столбцы через табуляцию, | или каждый с новой строки.', anchor='w').pack(fill='x', padx=12, pady=(12, 4))
    entry = tk.Text(window, height=10, wrap='word', undo=True)
    entry.pack(fill='both', expand=True, padx=12)
    tk.Label(window, text='Предпросмотр: в интерфейсе разметки будет только этот текст.', anchor='w').pack(fill='x', padx=12, pady=(12, 4))
    preview = tk.Text(window, height=10, wrap='word', state='disabled')
    preview.pack(fill='both', expand=True, padx=12)
    status = tk.StringVar(value='Оценка в звёздах и готовые метки в файл не включаются. ID партии назначим позднее.')
    tk.Label(window, textvariable=status, anchor='w', wraplength=800).pack(fill='x', padx=12, pady=8)

    def parse():
        task = convert(entry.get('1.0', 'end'))
        preview.configure(state='normal')
        preview.delete('1.0', 'end')
        preview.insert('1.0', task['data']['text'])
        preview.configure(state='disabled')
        return task

    def show():
        try:
            parse()
        except ValueError as exc:
            messagebox.showerror('Проверь строку', str(exc))

    def save():
        try:
            task = parse()
        except ValueError as exc:
            messagebox.showerror('Проверь строку', str(exc))
            return
        destination = filedialog.asksaveasfilename(
            title='Сохранить задание для Label Studio',
            initialfile=f"wb_{task['data']['source_review_id']}.json",
            defaultextension='.json', filetypes=[('JSON', '*.json')])
        if not destination:
            return
        # Check every JSON task in the chosen folder, including renamed files.
        source_id = str(task['data']['source_review_id'])
        destination_path = Path(destination)
        for existing in destination_path.parent.glob('*.json'):
            try:
                saved = json.loads(existing.read_text(encoding='utf-8-sig'))
            except (OSError, ValueError):
                continue
            saved = saved if isinstance(saved, list) else [saved]
            for item in saved:
                if not isinstance(item, dict):
                    continue
                data = item.get('data', {})
                if isinstance(data, dict) and str(data.get('source_review_id', '')) == source_id:
                    messagebox.showwarning('Отзыв уже сохранён',
                        f'Отзыв WB {source_id} уже находится в файле:\n{existing}\n\nПовтор не сохранён.')
                    status.set(f'Повтор: WB {source_id} уже сохранён в {existing.name}.')
                    return
        if destination_path.exists():
            messagebox.showwarning('Файл уже существует',
                'Выберите другое имя. Существующий файл не будет перезаписан.')
            return
        try:
            with destination_path.open('x', encoding='utf-8') as output:
                output.write(json.dumps([task], ensure_ascii=False, indent=2) + '\n')
        except OSError as exc:
            messagebox.showerror('Не удалось сохранить', str(exc))
            return
        status.set(f'Сохранено: {destination}. В Label Studio: Import → Upload Files → этот JSON.')

    buttons = tk.Frame(window)
    buttons.pack(pady=(0, 12))
    tk.Button(buttons, text='Предпросмотр', command=show).pack(side='left', padx=6)
    tk.Button(buttons, text='Сохранить JSON', command=save).pack(side='left', padx=6)
    window.mainloop()


if __name__ == '__main__':
    main()
