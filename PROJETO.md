# TIBIA BAGUA — estado do projeto

Documento de referência para discutir ideias. Descreve o que existe hoje, o que dá
para mexer, o que **não** pode quebrar, e o que ainda não foi verificado.

Última atualização: 5 de setembro de 2026.

---

## 1. O que é

Um servidor Tibia completo rodando **só na sua máquina** (`127.0.0.1`), com o
datapack global do OTServBR — o mundo inteiro, não um mapa vazio. Nada é exposto
para fora do computador: sem firewall aberto, sem port forwarding, sem IP público.

| Peça | O que é | Versão |
|---|---|---|
| **Canary** | O servidor (C++), fork do OTServBR-Global | protocolo **15.25** |
| **OTClient Redemption** | O cliente gráfico (C++/Lua) | assets **15.25** |
| **login-server** | Ponte HTTP/gRPC entre cliente e servidor (Go) | — |
| **MariaDB** (XAMPP) | Banco: contas, personagens, casas, mercado | — |

---

## 2. Como rodar

Tudo por duplo clique, na raiz do projeto:

| Atalho | O que faz |
|---|---|
| `JOGAR.bat` | Sobe MySQL → Canary → login-server → abre o jogo já logado |
| `EDITOR-MAPA.bat` | Editor de mapa, abre no templo de Thais |
| `EDITOR-SPRITE.bat` | Canary Studio + LibreSprite |
| `REFERENCIA-MONSTROS.html` | Busca: nome do monstro/NPC → LookType |
| `BACKUP.bat` / `RESTAURAR.bat` | Snapshot e volta atrás |

Conta `admin` / senha `admin123` / personagem **Admin** (level 100).

Portas: `3306` MySQL · `7171` e `7172` Canary · `8088` login-server.

---

## 3. Como as peças conversam

```
OTClient  --HTTP:8088-->  login-server  --:7172-->  Canary
   |                           |                       |
   |                       MySQL:3306 <----------------+
   |
   +--TCP:7172 (protocolo 15.25, XTEA + RSA)--> Canary
```

O login é HTTP (retorna session key + lista de personagens). O jogo em si é o
protocolo binário do Tibia na 7172.

**Ponto crítico:** servidor e cliente precisam concordar sobre quais itens existem
e que aparência têm. Os dois carregam o **mesmo** `appearances.dat`
(4.862.287 bytes). Se divergirem, o jogo quebra com `invalid item id`.

| Arquivo | Onde |
|---|---|
| `appearances.dat` (servidor) | `C:\dev\canary_run\data\items\` |
| `appearances-<hash>.dat` (cliente) | `otclient-src\data\things\1525\` |
| `catalog-content.json` | `otclient-src\data\things\1525\` |
| `sprites-<hash>.bmp.lzma` × 4.927 | `otclient-src\data\things\1525\` |
| `otservbr.otbm` (mapa, 176 MB) | `C:\dev\canary_run\data-otservbr-global\world\` |

---

## 4. O que já existe de conteúdo

Não estamos partindo do zero. O datapack global traz:

| | Quantidade |
|---|---|
| Monstros (`.lua`) | **1.655** |
| NPCs (`.lua`) | **1.033** |
| Quests (pastas de script) | **114** |
| Spells (`.lua`) | **591** |
| Actions | 88 |
| Movements | 39 |
| Creaturescripts | 25 |
| Globalevents | 8 |
| Raids | 21 |
| World changes | 6 |
| Objetos (appearances) | **42.107** (54.266 IDs) |
| Outfits | **1.443** (1.949 IDs) |
| Efeitos / missiles | 242 / 62 |
| Casas no mapa | 995 |
| Bosses / achievements | 438 / 356 |

Vocações: None, Sorcerer, Druid, Paladin, Knight, **Monk** — com promoções
(Master Sorcerer, Elder Druid, Royal Paladin, Elite Knight, Exalted Monk) e os
gems de cada uma.

Sistemas do Tibia moderno já presentes: bestiary, bosstiary, forge, imbuements,
familiars, mounts, attached effects, hazard/primal, wheel of destiny, market,
prey, taskboard.

---

## 5. Onde dá para mexer

Do mais fácil para o mais trabalhoso:

### 5.1 Números do jogo — minutos, sem risco

`C:\dev\canary_run\config.lua`

Hoje está tudo em **rate 1** (exp, skill, loot, magic, spawn) e `worldType = "pvp"`,
`protectionLevel = 7`, `deathLosePercent = -1`.

`C:\dev\canary_run\data\stages.lua` tem experiência por faixa de level
(hoje 7x até level 8, 6x até 20, 5x até 50, e cai daí).

Mexer aqui é editar texto e reiniciar o servidor. É o caminho para transformar
num servidor "high rate" ou deixar mais hardcore.

### 5.2 Monstros e NPCs — fácil, com interface

`data-otservbr-global/monster/` e `/npc/` — Lua legível: vida, exp, loot, ataques,
defesas, elementos, imunidades, diálogo e loja dos NPCs.

O **Canary Studio** abre esses `.lua` numa interface (Editor de Monstros / de NPCs),
então dá para mexer sem editar código.

### 5.3 Mapa — médio, visual

`EDITOR-MAPA.bat`. Pintar terreno, construir, posicionar itens, monstros e NPCs.
O mapa inteiro do Tibia global já está lá para modificar ou expandir.

### 5.4 Sprites — médio, ciclo de ida e volta

Exportar PNG no Canary Studio (aba Textura → ↓ PNG) → desenhar no LibreSprite →
importar → compilar. Detalhado no `GUIA-EDICAO.pdf`.

### 5.5 Scripts e sistemas novos — trabalhoso, mas é onde mora o "seu" servidor

`data-otservbr-global/scripts/` e `data/scripts/` — actions, talkactions,
creaturescripts, globalevents, movements, spells. É Lua puro, recarregado ao
reiniciar. Aqui dá para criar quest própria, evento automático, comando novo,
sistema de recompensa etc.

### 5.6 O próprio servidor — pesado

Código C++ em `C:\dev\canary`, compilável (VS 2026 + vcpkg + Ninja).
Só vale quando a mudança não é possível em Lua.

---

## 6. Regras que não podem ser quebradas

1. **Servidor e cliente têm que ter o mesmo `appearances.dat`.** Editar o desenho
   de um outfit existente é seguro. Adicionar ou remover IDs exige atualizar
   **os dois lados**.
2. **O Canary só lê o mapa e os `.lua` ao iniciar.** Salvar no editor não muda o
   jogo que está rodando — tem que reiniciar.
3. **LookTypes são compartilhados.** O outfit 22 é usado por Cyclops, Animated
   Cyclops, Juvenile Cyclops e o NPC A Sweaty Cyclops. Redesenhar muda os quatro.
   Confira em `REFERENCIA-MONSTROS.html`.
4. **119 criaturas usam aparência de item** (`lookTypeEx`), não outfit — não
   aparecem na lista de Outfits e não são editáveis por lá.
5. **Rodar `BACKUP.bat` antes de compilar sprites.** Esse passo reescreve arquivos
   que o jogo precisa para abrir.

---

## 7. Estado atual: o que está verificado

### Verificado, funcionando

- Entrada no mundo com renderização correta (sprites, itens, NPCs, minimapa, chat)
- Login HTTP: session key, lista de personagens, seleção de mundo
- Editor de mapa abre o mapa real (176 MB) com os sprites 15.25 e renderiza Thais
- Canary Studio lê os assets: 42.107 objetos, 1.443 outfits — confirmado por CLI e pela interface
- LibreSprite abre e funciona
- `BACKUP.bat` e `RESTAURAR.bat` testados (listagem, cancelamento, cópia)
- Referência de monstros: 2.688 entradas conferidas contra os `.lua`

### Não verificado — os riscos conhecidos

- **Ciclo completo de sprite** (exportar → desenhar → importar → **compilar**).
  O passo de compilar nunca foi executado. É o mais arriscado da lista.
- **Ciclo completo de mapa** (editar → salvar → reiniciar → ver no jogo).
  Salvar um `.otbm` de 176 MB nunca foi exercitado.
- **`JOGAR.bat` a frio** depois da correção das esperas (`timeout` → `ping`).
  Se der `ERRO 10061`, é só rodar de novo.

### Pontas soltas

- O patch `autoEnterGame` no `characterlist.lua` do OTClient é local e não
  versionado. Se atualizar o cliente, some.
- Nunca descobri por que o perfil padrão do OTClient (`%APPDATA%`) travava no
  diálogo de idioma. Contornado com `--user-dir=C:/dev/otcprofile`.
- **Nada está em git.** Os `.bat`, docs, patch do cliente e configs não têm
  histórico. Se algo se perder, é do zero.
- `Lib\` e `Scripts\` na raiz do projeto são lixo do `pip install` (~15 MB).

---

## 8. Bugs reais já corrigidos (não reintroduzir)

| Problema | Causa | Correção |
|---|---|---|
| Não entrava no mundo | Cliente em **1511**, servidor em **1525**. A partir de 1520 o `level percent` virou u16; o cliente lia u8 e todo o pacote desalinhava | Instalados os assets 15.25 no cliente |
| Patches errados no Canary | Forcei checksum ADLER32; o OTClient usa **SEQUENCE** desde 1290 | Revertido para o original (`git checkout`) e recompilado |
| Driver MySQL do Go recusava senha vazia | DSN sem `allowNativePasswords` | Corrigido em `database.go` |
| `SERVER_NAME_MISMATCH` | `.env` divergia do `config.lua` | Alinhado |
| Taskboard: EventCallback inválido | Binário ~2 meses mais velho que o código | Recompilado |
| Build quebrava no vcpkg | Caminho com acento (`Área de Trabalho`) | Código movido para `C:\dev\canary` |

---

## 9. Direções possíveis

Ideias para discutir, com esforço e risco estimados.

### Baixo esforço, resultado imediato
- **Ajustar rates** (`config.lua` + `stages.lua`) para o estilo de jogo que você quer
- **Criar mais personagens/contas** para testar vocações diferentes
- **Comandos de GM**: o Admin é group 6, então já tem `/teleport`, `/summon` etc.
- **Testar os dois ciclos não verificados** (sprite e mapa) num backup, para tirar o risco da mesa

### Médio
- **Colocar o projeto em git** — protege o trabalho e permite desfazer com precisão
- **Editar um monstro do zero** (loot, ataques, vida) pelo Editor de Monstros
- **Criar uma área nova no mapa** — uma ilha, uma dungeon, uma cidade
- **Trocar o sprite de um monstro** para algo autoral (fechando o ciclo de sprites)

### Alto — "servidor próprio" de verdade
- **Quest autoral**: script Lua + área no mapa + NPC + recompensa
- **Sistema novo**: evento automático, arena, ranking, loja customizada
- **Monstro/boss inédito**: sprite novo + `.lua` + spawn + entrada no bestiary
- **Rebalanceamento**: mexer em spells (591 arquivos) e vocações

### Infra
- **Automatizar o restart** depois de editar (hoje é manual: fecha, roda `JOGAR.bat`)
- **Um "modo dev"**: servidor com rates altos e comandos liberados, separado do "modo jogo"
- **Empacotar** para rodar em outra máquina sem refazer tudo

---

## 10. Onde as coisas moram

| Item | Caminho |
|---|---|
| Projeto (atalhos, docs) | `...\CODE\TIBIA BAGUA\` |
| Servidor em execução | `C:\dev\canary_run\` |
| Código-fonte do Canary | `C:\dev\canary\` (limpo, sem modificações) |
| Cliente | `...\TIBIA BAGUA\otclient-src\` |
| Perfil do cliente | `C:\dev\otcprofile\` |
| Editor de mapa | `C:\dev\tools\rme\` |
| Canary Studio (código + build) | `C:\dev\tools\beats-editor\` |
| LibreSprite | `C:\dev\tools\libresprite\` |
| Assets p/ os editores | `C:\dev\tools\rme-assets\` (junction para `things\1525`) |
| PNGs de trabalho | `C:\dev\tools\sprites-trabalho\` |
| Backups | `C:\dev\backups\` |
| Scripts de apoio | `C:\dev\*.ps1`, `C:\dev\gerar_*.py` |

Espaço em disco: ~25 GB livres.

---

## 11. Documentos

| Arquivo | Para quê |
|---|---|
| `GUIA-EDICAO.pdf` | Guia ilustrado de edição, 23 páginas com telas reais |
| `EDITORES.md` | Referência rápida dos editores |
| `LEIA-ME.md` | Como jogar e o que foi corrigido para o jogo funcionar |
| `PROJETO.md` | Este documento |
