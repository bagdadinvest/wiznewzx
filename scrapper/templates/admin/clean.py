import os
import re
from collections import defaultdict

def remove_duplicate_messages(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    msgid_dict = defaultdict(list)
    output_lines = []
    current_block = []
    in_msgid_block = False
    msgid = None

    for line in lines:
        if line.startswith('msgid '):
            if in_msgid_block and msgid:
                msgid_dict[msgid].append(current_block)
            in_msgid_block = True
            msgid = line
            current_block = [line]
        elif line.strip() == '':
            if in_msgid_block and msgid:
                msgid_dict[msgid].append(current_block)
            current_block = []
            in_msgid_block = False
            msgid = None
        else:
            if in_msgid_block:
                current_block.append(line)

    # Handle the last block
    if in_msgid_block and msgid:
        msgid_dict[msgid].append(current_block)

    # Keep only the first occurrence of each msgid
    seen_msgids = set()
    for msgid, blocks in msgid_dict.items():
        if msgid not in seen_msgids:
            output_lines.extend(blocks[0])
            seen_msgids.add(msgid)
        else:
            print(f"Duplicate removed: {msgid.strip()}")

    # Write cleaned content back to the file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(output_lines)

if __name__ == "__main__":
    po_file_path = "/home/lofa/Desktop/newsagency/newspro/locale/ar/LC_MESSAGES/django.po"
    if os.path.exists(po_file_path):
        remove_duplicate_messages(po_file_path)
        print(f"Duplicates removed from {po_file_path}.")
    else:
        print(f"File not found: {po_file_path}")
