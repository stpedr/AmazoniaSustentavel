import json
import glob

notebooks = glob.glob('BuildPkl_Batch*.ipynb')

for nb_file in notebooks:
    print(f"Processing {nb_file}...")
    with open(nb_file, 'r', encoding='utf-8') as f:
        nb = json.load(f)
    
    modified = False
    for cell in nb.get('cells', []):
        if cell.get('cell_type') == 'code':
            new_source = []
            for line in cell.get('source', []):
                new_line = line.replace('.value', '[()]')
                if new_line != line:
                    modified = True
                new_source.append(new_line)
            cell['source'] = new_source
            
    if modified:
        with open(nb_file, 'w', encoding='utf-8') as f:
            json.dump(nb, f, indent=1, ensure_ascii=False)
        print(f"Updated {nb_file}")
    else:
        print(f"No changes in {nb_file}")
