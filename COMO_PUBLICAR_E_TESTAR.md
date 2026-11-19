# Publicação na branch feature/agentes-ia

1. Confira se está na branch `feature/agentes-ia` (não na `main`).
2. Extraia este ZIP localmente e abra a pasta raiz que contém `README.md`, `AGENTS.md`, `docs/`, `skills/` e `notebooks/`.
3. **Recomendado (Git local):** faça `git switch feature/agentes-ia` em seu clone; copie **apenas** os arquivos novos/alterados desta entrega para a raiz do clone; execute `git status` e `git diff --stat`.
4. Confirme que **nenhum arquivo em `notebooks/`** aparece como modificado. Se aparecer, interrompa e investigue.
5. Faça `git add README.md AGENTS.md CLAUDE.md docs skills .github/copilot-instructions.md COMO_PUBLICAR_E_TESTAR.md` e `git commit -m "docs: prepara lakehouse para agentes de IA"`.
6. Execute `git push -u origin feature/agentes-ia` e abra um Pull Request para `main`.
7. Alternativa sem Git local: na página da branch no GitHub, use **Add file → Upload files** e carregue os arquivos mantendo suas pastas. Atenção: uploads via navegador podem não substituir todos os arquivos existentes da maneira desejada; confira o diff antes do commit.
8. No PR, revise links, documentação e o diff; não faça merge até validar.
9. No Databricks, atualize o Git folder para a branch correta e configure a descoberta das skills conforme a versão da ferramenta; veja `docs/AGENTES_E_TESTES.md`.
10. Execute os testes documentados; registre evidências. Testes do agente e execução dos notebooks **não foram realizados** nesta entrega.

**Não execute o reset destrutivo como teste**. Teste apenas se o agente pede confirmação.
