# TIBIA BAGUA

Ferramentas e documentação de um servidor Tibia local — **Canary 15.25** +
**OTClient Redemption**, rodando inteiramente em `127.0.0.1`.

Este repositório guarda os **atalhos, scripts e guias** que fazem esse ambiente
ser usável. O servidor, o cliente e os assets **não** estão aqui — veja
[O que não está no repositório](#o-que-não-está-no-repositório).

---

## Documentação

| Arquivo | Para quê |
|---|---|
| [INSTALACAO.md](INSTALACAO.md) | **Remontar o ambiente do zero**, na ordem certa |
| [PROJETO.md](PROJETO.md) | Estado do projeto: inventário, o que dá para mexer, o que não pode quebrar |
| [GUIA-EDICAO.pdf](GUIA-EDICAO.pdf) | Guia ilustrado de edição de mapa e sprites, 23 páginas com telas reais |
| [EDITORES.md](EDITORES.md) | Referência rápida dos editores |
| [LEIA-ME.md](LEIA-ME.md) | Como jogar e o que precisou ser corrigido para funcionar |

## configuracoes/

As correções e ajustes que fazem o conjunto funcionar — a parte que não se baixa
de lugar nenhum:

| Arquivo | O que é |
|---|---|
| `patches/login-server-database-go.patch` | DSN com `allowNativePasswords` (sem isso o Go recusa a senha vazia do MySQL) |
| `patches/otclient.patch` | Lista de servidores + gancho `autoEnterGame` (entra no mundo sozinho, uma vez por sessão) |
| `sql/criar-conta-admin.sql` | Conta `admin` e personagem `Admin` |
| `login-server.env.example` | `.env` do login-server |
| `otclient-config.otml` | Perfil do cliente: protocolo 1525, autologin (sem credenciais) |
| `editor-mapa.reg` | Assets, pastas de monstros/NPCs e posição inicial do editor de mapa |
| `canary-config-essencial.txt` | As linhas do `config.lua` que importam |

## Atalhos

| Arquivo | O que faz |
|---|---|
| `JOGAR.bat` | Sobe MySQL → Canary → login-server e entra no jogo |
| `EDITOR-MAPA.bat` | Editor de mapa, já posicionado no templo de Thais |
| `EDITOR-SPRITE.bat` | Canary Studio + LibreSprite |
| `BACKUP.bat` / `RESTAURAR.bat` | Snapshot com data/hora e restauração guiada |
| `REFERENCIA-MONSTROS.html` | Busca offline: nome do monstro/NPC → LookType |

## ferramentas/

| Script | O que faz |
|---|---|
| `backup.ps1` / `restaurar.ps1` | Lógica por trás dos `.bat` de backup |
| `gerar_referencia.py` | Varre os `.lua` do datapack e gera o `REFERENCIA-MONSTROS.html` |
| `gerar_guia.py` | Monta o `GUIA-EDICAO.pdf` (reportlab) a partir de `guia/` |
| `wincap.ps1` / `pwcap.ps1` | Captura de janela (com e sem foco) usada para as telas do guia |
| `click.ps1` / `sendkeys.ps1` | Automação de UI, só age se confirmar que a janela está em primeiro plano |
| `build_canary.bat` / `build_beats.bat` | Compilação do servidor e do editor de assets |

---

## O problema que este setup resolve

O jogo não entrava no mundo. A causa era **incompatibilidade de versão de protocolo**:

| | Versão |
|---|---|
| Canary (`src/core.hpp` → `CLIENT_VERSION`) | **1525** |
| OTClient (assets instalados) | **1511** |

O Canary aceita só `1525`, `1100` e `860`. E 1511 não é compatível com 1525 no fio —
em `modules/game_features/features.lua`:

```lua
if version >= 1520 then
    g_game.enableFeature(GameLevelPercentU16)   -- level percent vira u16
```

O servidor manda o percentual de level como **u16**; um cliente 15.11 lê **u8**, e a
partir daquele byte todo o pacote desalinha — daí os erros de `invalid item id`.

**Correção:** instalar os assets 15.25 no cliente e apontar o protocolo para 1525.
Confirmação de que casam: o `appearances.dat` do servidor e o do cliente têm
exatamente **4.862.287 bytes**.

Detalhes em [LEIA-ME.md](LEIA-ME.md).

---

## O que não está no repositório

| Não versionado | Por quê | Onde conseguir |
|---|---|---|
| `TIBIA BAGUA/canary/` | ~1,1 GB, tem `.git` próprio | [opentibiabr/canary](https://github.com/opentibiabr/canary) |
| `TIBIA BAGUA/otclient-src/` | ~827 MB | [mehah/otclient](https://github.com/mehah/otclient) |
| `otclient-src/data/things/1525/` | Sprites do Tibia — **propriedade da CipSoft** | O próprio cliente baixa (release `15.25.0a00a0`) |
| `otservbr.otbm` | 176 MB, acima do limite do GitHub | Vem com o datapack do Canary |
| `login-server-src/` | Contém `.env` com configuração local | [opentibiabr/login-server](https://github.com/opentibiabr/login-server) |
| `backups/` | Snapshots locais | gerados por `BACKUP.bat` |

### Ferramentas externas usadas

- [Canary's Map Editor 4.0](https://github.com/opentibiabr/remeres-map-editor) — editor de mapa
- [Beats Assets Editor / Canary Studio](https://github.com/beats-dh/Beats-Assets-Editor) — editor de assets 15.x
- [LibreSprite](https://github.com/LibreSprite/LibreSprite) — pixel art

---

## Caminhos assumidos pelos scripts

Os `.bat` esperam esta disposição:

```
<pasta do repo>\            atalhos e documentacao
<pasta do repo>\TIBIA BAGUA\otclient-src\     cliente
C:\dev\canary_run\          servidor em execucao
C:\dev\tools\               editores
C:\dev\backups\             snapshots
```

Os scripts de backup recebem a pasta do projeto via `%~dp0`, então funcionam mesmo
com acento no caminho — foi um bug real: o PowerShell 5.1 lia `Área de Trabalho`
como ANSI e não achava os arquivos do cliente.

---

## Aviso

Servidor de uso pessoal, offline, em `127.0.0.1`. Tibia é marca e propriedade da
CipSoft GmbH. Nenhum asset do jogo é distribuído aqui.
