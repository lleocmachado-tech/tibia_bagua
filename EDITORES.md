# Editores — mapa e sprites

## 1. Editor de mapa — Canary's Map Editor (Remere's) v4.0

**Abrir:** duplo clique em `EDITOR-MAPA.bat`

Já vem configurado e apontando para o mapa real do servidor.

| Item | Valor |
|---|---|
| Programa | `C:\dev\tools\rme\canary-map-editor-v4.0-windows\canary-map-editor-x64.exe` |
| Mapa do servidor | `C:\dev\canary_run\data-otservbr-global\world\otservbr.otbm` (184 MB) |
| Backup do mapa | `otservbr.otbm.backup` (mesma pasta) |
| Sprites 15.25 | `C:\dev\tools\rme-assets` (junction para os assets do cliente) |
| Monstros | `C:\dev\canary_run\data-otservbr-global\monster` |
| NPCs | `C:\dev\canary_run\data-otservbr-global\npc` |

O mapa é grande: leva ~40 s para abrir e ocupa ~5,8 GB de RAM.

Ele abre numa coordenada vazia. Use **Ctrl+G** (ir para posição) e vá para
`32369, 32241, 7` (templo de Thais) para ver o mapa de verdade.

### Importante: como as edições chegam no jogo

O Canary lê o `.otbm` **só quando inicia**. Então:

1. Edite e salve no editor
2. Feche o servidor (janela do Canary)
3. Rode `JOGAR.bat` de novo

Se quebrar alguma coisa, restaure o backup:

```bash
copy /Y "C:\dev\canary_run\data-otservbr-global\world\otservbr.otbm.backup" "C:\dev\canary_run\data-otservbr-global\world\otservbr.otbm"
```

### Como foi configurado

O RME espera uma pasta de cliente no formato `<pasta>/assets/` + `<pasta>/package.json`.
Os assets do OTClient não vêm nesse formato, então montei:

```
C:\dev\tools\rme-assets\
  package.json          -> { "version": "15.25" }
  assets\               -> junction para otclient-src\data\things\1525
```

Os caminhos ficam no registro em `HKCU\Software\OpenTibiaBR\Canary Map Editor`
(seções `Version` e `Creatures`). Se precisar refazer pela interface:
**Edit > Preferences**.

---

## 2. Editor de sprites — personagens, monstros, efeitos

**Abrir:** duplo clique em `EDITOR-SPRITE.bat` (abre os dois programas juntos)

São **duas** ferramentas, porque nenhuma faz o trabalho todo:

| Programa | Para quê |
|---|---|
| **Canary Studio** (Beats-Assets-Editor) | Navegar/organizar os assets, achar o outfit, exportar e reimportar sprites, editar flags, editar `.lua` de monstros e NPCs |
| **LibreSprite** 1.1 | Desenhar de fato os pixels |

### Por que dois programas

O Canary Studio **não tem canvas de desenho**. Ele é um gerenciador de assets.
Olhando os comandos que ele expõe no backend, o fluxo é:

```
export_sprites_to_png  ->  (desenhar fora)  ->  import_image_as_tiles
                       ->  replace_appearance_sprites  ->  compile_imported_sprites
```

Então o ciclo real de trabalho é:

1. **Canary Studio** — na tela inicial, em **Client Path**, clique em `Browse` e
   selecione:

   ```
   C:\dev\tools\rme-assets
   ```

   (a raiz, **não** a subpasta `assets` — o app procura `<path>\assets\catalog-content.json`.
   É a mesma pasta que o editor de mapa usa.)

   Depois entre em **Editor de Assets** → **Outfits** → clique no outfit →
   aba **Textura** → botão **↓ PNG**. Salve em `C:\dev\tools\sprites-trabalho`.

2. **LibreSprite** — abra o PNG e desenhe.
   Use o menu **Frame** para animação (outfit tem 4 direções + frames de andar).

3. **Canary Studio** — importe o PNG de volta, substitua os sprites do outfit e
   **compile** (isso regrava os spritesheets e o `catalog-content.json`).

> O Client Path **fica salvo** entre execuções — só precisa apontar uma vez.

### Atalho: descobrir o LookType sem abrir nada

Abra **`REFERENCIA-MONSTROS.html`** (duplo clique, roda offline no navegador).
São os **2.688** monstros e NPCs do servidor com busca instantânea.

- 2.564 usam **outfit** (editável no Canary Studio)
- 119 usam aparência de **item** (`lookTypeEx`, em amarelo) — esses não aparecem na lista de Outfits
- 5 não declaram aparência

> **Cuidado:** monstros diferentes dividem o mesmo LookType. O outfit **22** é usado por
> Cyclops, Animated Cyclops, Juvenile Cyclops **e** o NPC A Sweaty Cyclops — redesenhar
> muda os quatro. Busque o número na referência antes de editar.

### Backup e restauração

| Atalho | O que faz |
|---|---|
| `BACKUP.bat` | Cria `C:\dev\backups\<data_hora>\` com mapa + appearances (cliente e servidor) + catalog (~186 MB). Pergunta se quer incluir os 4.927 spritesheets (+88 MB). |
| `RESTAURAR.bat` | Lista os backups, você escolhe o número. Fecha os programas que travam os arquivos e exige digitar `SIM` para confirmar. |

Rotina: **BACKUP.bat → edite → teste no jogo → se quebrou, RESTAURAR.bat**.

### A exportação fica na aba Textura, não em "criaturas"

A tela de **criaturas** (World Data → 812 criaturas) mostra dados do bestiário —
dificuldade, ocorrência, LookType — e só tem o botão **Excluir**.
**Ela não exporta sprite.**

Use-a apenas para descobrir o **LookType** do monstro, que é o ID do outfit:

| Monstro | LookType | Onde editar o sprite |
|---|---|---|
| cyclops | 22 | Outfits → **Ir para ID** → 22 → aba **Textura** |

### O importador: tamanhos e transparência

- Aceita **32x32, 32x64, 64x32, 64x64**. Folhas maiores são fatiadas automaticamente.
- **Magenta puro (`#FF00FF`) = transparente.** É o chroma key que o importador usa.

### As outras duas telas

- **Monster editor** — aponte para `C:\dev\canary_run\data-otservbr-global\monster`
- **NPC editor** — aponte para `C:\dev\canary_run\data-otservbr-global\npc`

### O que o Canary Studio faz bem

- Interface em **português**, 6 temas
- Preview da animação dos outfits com controles de playback
- **Editor de monstros `.lua`**: loot, ataques, defesas, elementos, imunidades,
  bestiary e bosstiary — bem melhor que editar XML/Lua na mão
- Editor de NPCs com loja (shop)
- Merge de arquivos `.dat` com remapeamento de IDs

Está em **beta** — faça backup antes de mexer.

### Pasta de trabalho

`C:\dev\tools\sprites-trabalho` — deixei criada para os PNGs exportados,
para não espalhar arquivo solto dentro da pasta de assets.

### Alternativa (deixei instalada, mas não é a principal)

`C:\dev\tools\AssetsEditor\AssetsEditor\Assets Editor.exe` — o *Assets Editor 2.0*.
É de novembro de 2023 (anterior ao 15.x) e não guarda o caminho dos assets, por
isso não é o principal. Só vale por um recurso que o Canary Studio não tem:
**exportar assets modernos para o formato legado `.dat`/`.spr` do 8.60**.

### Instalador

Se quiser instalar o Canary Studio no sistema (em vez de rodar da pasta de build):
`C:\dev\tools\beats-editor\src-tauri\target\release\bundle\nsis\Canary Studio_0.1.0_x64-setup.exe`

---

## Onde ficam os sprites

Os sprites de 15.x não são mais `.spr`/`.dat` como no Tibia antigo. Hoje são:

| Arquivo | O que é |
|---|---|
| `appearances-<hash>.dat` | protobuf com todos os objetos, **outfits** (personagens/monstros), efeitos e missiles |
| `catalog-content.json` | índice que liga cada sprite ao seu spritesheet |
| `sprites-<hash>.bmp.lzma` | os spritesheets em si (4927 arquivos), comprimidos em LZMA |

Tudo isso está em:
`TIBIA BAGUA\otclient-src\data\things\1525\`

**Personagens e monstros = "outfits"** dentro do `appearances.dat`.

### Atenção ao editar sprites

O servidor e o cliente precisam concordar. O `appearances.dat` existe em dois lugares:

- Cliente: `otclient-src\data\things\1525\appearances-<hash>.dat`
- Servidor: `C:\dev\canary_run\data\items\appearances.dat`

Hoje os dois são **o mesmo arquivo** (4.862.287 bytes). Se você alterar sprites
no cliente, os IDs precisam continuar batendo com os do servidor — senão volta o
problema de "invalid item id" que quebrou a entrada no jogo antes.

Regra prática: **editar a aparência (pixels) de um outfit existente é seguro.
Adicionar/remover IDs exige atualizar os dois lados.**
