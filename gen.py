import sys

with open('C:\\Users\\hp\\Desktop\\Pani Pilo\\localhost-url-access-inquiry\\python_backend\\bad_words.txt', 'r', encoding='utf-8') as f:
    text = f.read()
    
# Split by \n (both actual newlines and literal '\n' if any)
words = text.replace('\\n', '\n').split('\n')
words = [w.strip() for w in words if w.strip()]

# Remove duplicates
words = list(dict.fromkeys(words))

out = 'const PROFANITY: { word: string; lang: string }[] = [\n'
for w in words:
    out += f'  {{ word: "{w}", lang: "Detected" }},\n'
out += '];\n'

with open('C:\\Users\\hp\\Desktop\\Pani Pilo\\localhost-url-access-inquiry\\scratch_out.txt', 'w', encoding='utf-8') as f:
    f.write(out)
print("Done!")
