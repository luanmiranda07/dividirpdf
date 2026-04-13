
# DivisorPDF

Aplicativo em Python com interface gráfica para dividir arquivos PDF de forma simples e local, sem depender de sites externos e sem limitações artificiais de tamanho como as de algumas plataformas online.

## Funcionalidades

O sistema permite dividir PDFs de 4 formas:

- **Um arquivo por página**
- **A cada X páginas**
- **Por intervalos personalizados**
- **Por palavra-chave**

## Vantagens

- Funciona localmente no computador
- Não precisa enviar arquivos para a internet
- Sem limite artificial de tamanho
- Interface simples e prática
- Geração de executável `.exe` para Windows

## Tecnologias utilizadas

- Python 3
- Tkinter
- pypdf
- PyInstaller

## Requisitos

Antes de executar o projeto em Python, instale:

```bash
pip install pypdf
```


## Como gerar o executável `.exe`

Foi utilizado o seguinte comando para gerar o executável com ícone:

<pre class="overflow-visible! px-0!" data-start="983" data-end="1092"><div class="relative w-full mt-4 mb-1"><div class=""><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-token-bg-elevated-secondary corner-superellipse/1.1 overflow-clip rounded-3xl lxnfua_clipPathFallback"><div class="pointer-events-none absolute inset-x-4 top-12 bottom-4"><div class="pointer-events-none sticky z-40 shrink-0 z-1!"><div class="sticky bg-token-border-light"></div></div></div><div class="relative"><div class="w-full overflow-x-hidden overflow-y-auto"><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼs ͼ16"><div class="cm-scroller"><div class="cm-content q9tKkq_readonly"><span>pyinstaller </span><span class="ͼ12">--noconfirm</span><span></span><span class="ͼ12">--clean</span><span></span><span class="ͼ12">--onefile</span><span></span><span class="ͼ12">--windowed</span><span></span><span class="ͼ12">--name</span><span></span><span class="ͼz">"DivisorPDF"</span><span></span><span class="ͼ12">--icon</span><span></span><span class="ͼz">"pdf.ico"</span><span> main.py</span></div></div></div></div></div></div></div></div></div></div></div></div></div></pre>

## Como usar

1. Abra o programa
2. Selecione o arquivo PDF
3. Escolha a pasta de saída
4. Escolha o modo de divisão
5. Configure os campos necessários
6. Clique em **Dividir PDF**

## Modos de divisão

### 1. Um arquivo por página

Cada página do PDF original será salva como um arquivo PDF separado.

Exemplo:

* página 1 → `arquivo_001.pdf`
* página 2 → `arquivo_002.pdf`

### 2. A cada X páginas

Divide o PDF em blocos com a quantidade de páginas definida pelo usuário.

Exemplo:

* se escolher `2`, o sistema cria:
* páginas 1 e 2
* páginas 3 e 4
* páginas 5 e 6

### 3. Por intervalos personalizados

Permite informar intervalos específicos de páginas.

Exemplo:

<pre class="overflow-visible! px-0!" data-start="1853" data-end="1879"><div class="relative w-full mt-4 mb-1"><div class=""><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-token-bg-elevated-secondary corner-superellipse/1.1 overflow-clip rounded-3xl lxnfua_clipPathFallback"><div class="pointer-events-none absolute end-1.5 top-1 z-2 md:end-2 md:top-1"></div><div class="relative"><div class="w-full overflow-x-hidden overflow-y-auto pe-11 pt-3"><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼs ͼ16"><div class="cm-scroller"><div class="cm-content q9tKkq_readonly"><span>1-3, 4-6, 7-10</span></div></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></pre>

### 4. Por palavra-chave

O sistema procura uma palavra ou expressão dentro do PDF e cria uma nova divisão sempre que ela aparece.

Exemplo de palavra-chave:

<pre class="overflow-visible! px-0!" data-start="2040" data-end="2060"><div class="relative w-full mt-4 mb-1"><div class=""><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-token-bg-elevated-secondary corner-superellipse/1.1 overflow-clip rounded-3xl lxnfua_clipPathFallback"><div class="pointer-events-none absolute end-1.5 top-1 z-2 md:end-2 md:top-1"></div><div class="relative"><div class="w-full overflow-x-hidden overflow-y-auto pe-11 pt-3"><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼs ͼ16"><div class="cm-scroller"><div class="cm-content q9tKkq_readonly"><span>UNIDADE:</span></div></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></pre>

Esse modo funciona melhor em PDFs com texto selecionável.

## Observações importantes

* O modo **por palavra-chave** depende de o PDF conter texto legível.
* Se o PDF for escaneado como imagem, a busca por palavra-chave pode não funcionar sem OCR.
* Para melhor compatibilidade, utilize arquivos PDF com texto pesquisável.

## Estrutura sugerida do projeto

<pre class="overflow-visible! px-0!" data-start="2421" data-end="2494"><div class="relative w-full mt-4 mb-1"><div class=""><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-token-bg-elevated-secondary corner-superellipse/1.1 overflow-clip rounded-3xl lxnfua_clipPathFallback"><div class="pointer-events-none absolute end-1.5 top-1 z-2 md:end-2 md:top-1"></div><div class="relative"><div class="w-full overflow-x-hidden overflow-y-auto pe-11 pt-3"><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼs ͼ16"><div class="cm-scroller"><div class="cm-content q9tKkq_readonly"><span>DivisorPDF/</span><br/><span>│</span><br/><span>├── main.py</span><br/><span>├── pdf.ico</span><br/><span>├── README.md</span><br/><span>└── dist/</span></div></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></pre>

## Objetivo do projeto

Este projeto foi criado para facilitar a divisão de PDFs grandes de maneira rápida, prática e sem depender de serviços online, atendendo principalmente cenários em que há necessidade de separar documentos por páginas, blocos, intervalos ou conteúdo textual.

## Melhorias futuras

* Nomear arquivos automaticamente com base no conteúdo
* Suporte a OCR para PDFs escaneados
* Mais opções de personalização na interface
* Histórico de arquivos processados

## Autor

Projeto desenvolvido por  **Luan Miranda** .
