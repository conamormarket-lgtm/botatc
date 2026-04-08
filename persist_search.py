import re
with open("inbox.html", "r", encoding="utf-8") as f:
    text = f.read()

old_logic = "document.getElementById('chatSearchInput')?.addEventListener('input', window.aplicarFiltroChats);"

new_logic = '''
        const searchInp = document.getElementById('chatSearchInput');
        if (searchInp) {
            const savedSearch = sessionStorage.getItem('chatSearchValue');
            if (savedSearch) {
                searchInp.value = savedSearch;
                // Wait for DOM to finish then apply
                setTimeout(() => { if(window.aplicarFiltroChats) window.aplicarFiltroChats(); }, 100);
            }
            
            searchInp.addEventListener('input', function(e) {
                sessionStorage.setItem('chatSearchValue', this.value);
                if(window.aplicarFiltroChats) window.aplicarFiltroChats();
            });
        }
'''

if "sessionStorage.getItem('chatSearchValue')" not in text:
    text = text.replace(old_logic, new_logic)
    with open("inbox.html", "w", encoding="utf-8") as f:
        f.write(text)
    print("Fixed search context retention")
