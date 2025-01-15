
# Název úlohy

V předchozích úlohách jste se dozvěděli, jak funguje počítač (von neumanova koncepce) - procesor postupně čte a vykonává příkazy uložené (v dnešních implementacích) v bajtech. Cílem této úlohy bude si naprogramovat emulátor takového procesoru. <TODO: Procesoru/emulátoru??>

## Technické parametry procesoru
V této úloze budeme emulovat procesor řady x86.

### Registry
Během vykonávání programu si chceme udržovat proměnné, se kterými pracujeme. Ty by se daly psát do paměti, jenomže taková operace velmi pomalá (pokud chcete provádět několik tisíc <TODO: koli??> operací za sekundu), proto jsou přímo u jádra procesoru zabudované speciální paměti, se kterými manipulovat je mnohem rychlejší.

#### Všeobecné registry
Tyto registry vývojářům slouží jako místo pro ukládání mezivýsledků a proměnných. Náš procesor má 4 16-bitové všeobecné registry, označené `AX`, `BX`, `CX`, `DX`.  Protože starší procesory pracovaly pouze s 8-bitovými registry a bylo žádoucí zachovat zpětnou kompatibilitu (program určený pro 8-bitový procesor můžete spustit i na 16-bitovém procesoru), na jeden tento 16-bitový registr lze nahlížet jako na dva 8-bitové registry a to tak, že `AX` je složen z `AH` a `AL` (H a L znamená High a Low).
<TODO: Add obrázek>

#### Segmentové registry
Samozřejmě je možné celý kód psát jako jednu velikou hromadu bajtů, kde jsou naházené bajty instrukcí a dat, je ale lepší si kód členit do tzv. segmentů. Např. si můžeme vytvořit segment `code`, kam budeme ukládat instrukce k našemu programu a segment `data` pro proměnné. (Ve skoro všech programech existuje ještě segment `stack`, k němu se však dostaneme až v další úloze 😉).
Výhodou používání segmentů je, že v moderních procesorech na ně můžeme aplikovat ochranu pro čtení a psaní. Například nechceme, aby se stalo, že náš program začne vykonávat instrukce z datového segmentu kam ukládáme vstup od uživatele (který by sem mohl uložit vlastní kód a způsobit <TODO: dopsat>).
Pro jednodušší práci se segmenty výrobci nachystali registry `CS` - code segment, `DS`- data segment, `SS` - stack segment a `ES` - extra segment určený další segment.

#### Řídící registry
Váš prgram bude ležet někde v paměti a procesor aby instrukce přečetl, si musí o tato data požádat. Procesor zná adresu prvního bajtu vašeho programu, <TODO: dopsat IP>

Vývojáři procesoru si vymysleli ještě jeden speciální registr `F` - flags. Tento 16-bitový registr v sobě obsahuje "metadata" o provedených instrukcích, kde jednotlivé bity mají svůj význam. Zde si popíšeme některé užitečné:

- Carry flag `CF`: Ten obsahuje přenos z nejvyššího bitu (bude dávat smysl později).
- Parity flag `PF`: Obsahuje `1`, pokud má dolní osmice výsledku sudý počet jedniček.
- Zero flag `ZF`: Obsahuje `1`, je výsledkem operace nula.
- Sign flag `SF`: Obsahuje `1`, je-li výsledek v doplňkovém kódu záporný. 
- Overflow flag `OF`: Obsahuje `1`, pokud došlo k přetečení. Výhodou je, že pro používání tohohle `OF` nemusíte platit.
- Ostatní bity mají také svůj význam, ale jsou mimo rozsah této vlny.

<TODO: ADD image zásobníku a idexů >
Pro lepší představu, tady máte obrázek všech registrů našeho procesoru:
<TODO: ADD image všech registrů>



## Assembly
Jak již bylo několikrát zmíněno, procesor pracuje s bajty. Nic vám samozřejmě nebrání psát celý svůj kód pouze v jedničkách a nulách, či v šestnástkové soustavě, je ovšem mnohem pohodlnější a psát program ve člověku čitelné podobě. Od toho máme jazyk `assembly`, který je prakticky vizuální forma programu + se do něj dají psát komentáře, navíc si umí poradit s "proměnnými". Podobně, jako většinu programovacích jazyků pro spuštění musíte zkompilovat (* upřesnění pro zajímavost v rozbalovacím textu pod tímto odstavcem) i kód v assembly je nutno převést na jednotlivé bajty. Tomuto procesu se říká skládání (anglicky assembling) a program který to dělá se jmenuje assembler. <TODO: přepsat tenot odstavec>

### Základní struktura souboru
Nejprve se pojďme podívat na základní strukturu programu.

Všechno se ukládá do segmentů. Ten začíná řádkem `segment <nazev_segmentu> a je ukončen začátkem jiného segmentu, nebo koncem souboru.


Na jiné řádky než označení segmentu se píšou instrukce. Instrukce mají zpravidla dvě nebo tři písmena a vždy jsou odsazené na první zarážku (před instrukcí je právě jeden tabulátor). K některým instrukcím se vážou argumenty (podobně jako k funkcím v pythonu). Ty se mezi sebou oddělují čárkou a mezi instrukcí a prvním argumentem je mezera. 
Samozřejmě je možné psát i komentáře. Ty místo pythonovského `#` používají `;`, jinak fungují stejně. Doporučuje se všechny komentáře zarovnávat na stejnou odrážku.

Řádek s instrukcí si můžeme pojmenovat tzv. návěšťím. Pokud se někde v programu budeme chtít na tento řádek odkázat, použijeme jeho návěšťí. Při skládání (kompilaci) programu se pak tento ukazatel převede na index daného požadovaného bajtu v segmentu.

Existuje ale jedno speciální návěšťí, které musí obsahovat každý program. Tím je návěšťí `..start`, které říká, od které instrukce se má začít kód vykonávat. Jinak se program vykonává od prvního bajtu - tam ale v složitějších programech bývá něco jiného (více v úloze přerušení).

Zde je ukázkový kód pro sečtení dvou proměnných. Využívá instrukce `MOV`, `ADD` a klíčové slovo `db`, o kterých si detailně povíme níže zatím je chápat nemusíte. 
Ve zkratce instrukce `MOV` (move) ukládá do registrů a paměti, instrukce `ADD` přičte k prvnímu registru druhý a klíčové slovo `db` (define byte) vytvoří bajt dané hodnoty.

``` asm
segment	code
..start MOV AX, [var_a]   ; Do registru AX načte proměnnou var_a z datového segmentu 
    MOV BX, [var_b]   ; Snad z předchozího řádku uhádnete význam tohoto

    ADD AX, BX  ; K registru AX přičte BX (V pythonu něco jako AX += BX)

    HLT ; Konec programu

segment data
var_a    db 40  ; Hodnoty, které mají být sečteny
var_b    db 2

```

#### Instrukce
V této sekci se seznámíme s jednotlivými instrujcemi. 
Začneme s tou asi nejsložitější, ale nejpotřebnější instrukcí, tak se nenechte odradit 😃.

##### MOV
Instrukce `MOV`, neboli _move_, přenáší data vodněkaďs někam. Má několik variant podle toho vodkaďs kam (významy vysvětleny níže):

- `MOV r/m8,r8`
- `MOV r/m16,r16`
- `MOV r8,r/m8`
- `MOV r16,r/m16`
- `MOV r/m16,segmentový registr`
- `MOV segmentový registr,r/m16`
- `MOV r/m8,imm8`
- `MOV r/m16,imm16`

Kde `r8` znamená 8-bitový registr (tedy např. `AL`, nebo `DH`), `r16` asi logicky odvodíte, že označuje 16-bitový registr (tedy třeba `AX`). `imm8` je nějaká konstanta (například `MOV AX, 42` načte do registru `AX` číslo 13). V ukázkovém programu výše jste viděli, že jsme do registru načítali hodnotu z paměti - to zde značíme `m8` nebo `m16`, píše se v hranatých závorkách (např. `MOV AX, [var_a]`).

Takže tohle jsou validní instrukce:
Schválně si zkuste odhadnout co dané instrukce dělají a ověřte si to v komentáři. 
```
    MOV AL, 42  ; Do registru AL vloží hodnotu 42 (binárně 00101010)
    MOV AX, 42  ; Do registru AX vloží hodnotu 42 (binárně 00000000 00101010)
    
    MOV AL, DL  ; Do registru AL zkopíruje obsah registru DL
    MOV AX, DX  ; Do registru AX zkopíruje obsah registru DX

    MOV AL, [20]   ; Do registru AL zkopíruje obsah dvacátého bajtu z datového segmentu
    MOV AX, [20]   ; Do registru AL zkopíruje obsah dvacátého bajtu z datového segmentu
                    ; A zároveň do registru AH zkopíruje obsah jednadvacátého bajtu z ds

    MOV AL, [navesti]   ; <TODO: už se mi to nechce psát>

    MOV [20], DL    ; Do datového segmentu na dvacátý bajt vloží hodnotu DL
    MOV [20], DX    ; Do datového segmentu na dvacátý bajt vloží hodnotu DH
                    ; a zároveď na jednadvacátý bajt vloží DL

```

! Pozor, zde jsou příklady častých chyb:
```
    MOV AX, CL  ; ŠPATNĚ - registr AX je 16-bitový, registr CL 8-bitový

    MOV AL, 400 ; ŠPATNĚ - číslo 400 se nevejde do 8 bitů

    MOV [promenna], 42  ; ŠPATNĚ - má se vložit 42 na jeden, dva nebo čtyři bajty??
    MOV [promenna], byte 42 ; Tohle už je cajk. Říkáte, že to je na jeden byte
    MOV [promenna], word 42 ; Taky cajk. Word znamená 16 bitů
    MOV [promenna], doubleword 42 ; Taky cajk. Word znamená 32 bitů
```
Instrukce `MOV` nijak nemění žádný flag registru `F`. (Tato informace se bude hodit později)

Zde doporučuji udělat si první úkol, kde se dozíte, jestli tuto instrukci správně chápete.


##### ADD
Instrukce `ADD` má tyto varianty:

- `r/m8,imm8`
- `r/m16,imm16`
- `r/m16,imm8`
- `r/m8,r8 `
- `r/m16,r16 `
- `r8,r/m8`
- `r16,r/m16`

s těmito význami
```
    ADD AX, 3   ; Do registru AX uloží AX + 3
    ADD AL, 3   ; Do registru AL uloží AL + 3

    ADD AL, BL  ; Do registru AL uloží AL + BL
    ADD AX, BX  ; Do registru AL uloží AL + BL

    ADD AL, [navesti]   ; Do registru AL uloží AL + hodnota bajtu na adrese navesti z datového segnentu
    ADD AL, [20]   ; Do registru AL uloží AL + hodnota bajtu na adrese 20 datového segnentu

    ADD AX, [navesti]   ; Do registru AX uloží AX + hodnota slova (slovo jsou dva bajty) na adrese navesti z datového segnentu
    ADD AX, [20]    ; to samé

    ADD [20], byte 42   ; Zvýší hodnotu bajtu datového segmentu na adrese 20
    ADD [20], word 42   ; Zvýší hodnotu slova (dva bajty) datového segmentu na adrese 20
                        ; Obdobně to samozřejmě funguje s návěštím
```
Ale zase pozor:
```
    MOV [navesti], 42   ; ŠPATNĚ - opět neví, jestli na danou adresu vložit jeden, dva nebo čtyři bajty
    MOV [navesti], byte 42  ; Už je cajk
```

Podle výsledku upravuje tyto registry:  `OF`, `SF`, `ZF`, `PF`, `CF`

Opět je na tuto instrukci udělaný odpovědík. Zkuste si ho, než se vrhnete na další instrukce.

##### ADC
Instrukce `ADC` (add with carry) funguje úplně stejně jako `ADD`, akorát pokud je v registru `F` nastavený `CF` (carry flag) na `1`, přičte k výsledku navíc ještě 1.

Stejně jako instrukce `ADD` upravuje tyto registry:  `OF`, `SF`, `ZF`, `PF`, `CF`

##### SUB
Instrukce `SUB` funguje stejně jako 

