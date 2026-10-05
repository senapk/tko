"""Educational synchronization of a student's origin/main repository."""

from __future__ import annotations

from tko.git.console import SyncReporter, translate
from tko.git.repository import GitError, GitSyncOps


class UserCancelled(Exception):
    """The user declined a step or a merge needs manual resolution."""


class MergeCompleted(Exception):
    """A pending merge was completed; sync resumes on the next invocation."""


class SyncApplication:
    def __init__(
        self, repository: GitSyncOps, console: SyncReporter,
        allowed_branch: str = "main", remote: str = "origin",
    ) -> None:
        self.repository: GitSyncOps = repository
        self.console: SyncReporter = console
        self.allowed_branch: str = allowed_branch
        self.remote: str = remote

    def validate_environment(self) -> None:
        self.console.step(translate("Validando ambiente", "Checking environment"))
        if not self.repository.is_repository():
            raise GitError(translate(
                "Este diretório não é um repositório Git.",
                "This directory is not a Git repository.",
            ))
        self.console.success(translate("Repositório Git detectado", "Git repository found"))

    def validate_remote(self) -> None:
        self.console.step(translate("Verificando remoto", "Checking remote"))
        if not self.repository.has_remote(self.remote):
            raise GitError(translate(
                f"Remoto '{self.remote}' não configurado.",
                f"Remote '{self.remote}' is not configured.",
            ))
        self.console.success(translate("Remoto configurado", "Remote configured"))

    def validate_branch(self) -> str:
        branch: str = self.repository.current_branch()
        if branch != self.allowed_branch:
            raise GitError(translate(
                f"Branch inválida: {branch}. Use {self.allowed_branch}.",
                f"Invalid branch: {branch}. Use {self.allowed_branch}.",
            ))
        return branch

    def show_unresolved_conflicts(self, conflicts: list[str]) -> None:
        if not conflicts:
            return
        self.console.step(translate(
            "Conflitos de merge ainda não resolvidos",
            "Unresolved merge conflicts",
        ))
        self.console.warn(translate(
            "Resolva manualmente estes arquivos:",
            "Resolve these files manually:",
        ))
        for file in conflicts:
            self.console.write(f"  - {file}")
        self.console.write(translate(
            "Opção 1: edite os arquivos e remova os marcadores de conflito.\n"
            "Opção 2: mantenha a versão local: git checkout --ours -- .\n"
            "Opção 3: mantenha a versão remota: git checkout --theirs -- .\n"
            "Depois execute tko git sync novamente.",
            "Option 1: edit the files and remove conflict markers.\n"
            "Option 2: keep the local version: git checkout --ours -- .\n"
            "Option 3: keep the remote version: git checkout --theirs -- .\n"
            "Then run tko git sync again.",
        ))

    def handle_pending_merge(self) -> None:
        if not self.repository.is_merge_in_progress():
            return
        self.console.step(translate("Finalizando merge pendente", "Finishing pending merge"))
        self.repository.stage_all()
        conflicts: list[str] = self.repository.conflicted_files()
        if conflicts:
            self.show_unresolved_conflicts(conflicts)
            raise UserCancelled
        self.repository.finish_merge()
        self.console.success(translate("Merge finalizado.", "Merge completed."))
        self.console.warn(translate(
            "Execute tko git sync novamente para continuar a sincronização.",
            "Run tko git sync again to continue synchronization.",
        ))
        raise MergeCompleted

    def setup_git_identity(self) -> None:
        self.console.step(translate("Verificando identidade Git", "Checking Git identity"))
        if not self.repository.get_config("user.name"):
            name: str = self.console.ask(translate("Digite seu nome: ", "Enter your name: "))
            if not name.strip():
                raise GitError(translate("O nome não pode ser vazio.", "The name cannot be empty."))
            self.repository.set_config("user.name", name)
        if not self.repository.get_config("user.email"):
            email: str = self.console.ask(translate("Digite seu email: ", "Enter your email: "))
            if not email.strip():
                raise GitError(translate("O email não pode ser vazio.", "The email cannot be empty."))
            self.repository.set_config("user.email", email)
        self.console.success(translate("Identidade Git configurada", "Git identity configured"))

    def show_status(self) -> None:
        self.console.step(translate(
            "Resumo do repositório (?? novo, M modificado, D removido, UU conflito)",
            "Repository status (?? new, M modified, D deleted, UU conflict)",
        ))
        self.repository.status()

    def ask_commit_message(self) -> str:
        while True:
            message: str = self.console.ask(translate("Mensagem do commit: ", "Commit message: "))
            if message.strip():
                return message
            self.console.error(translate(
                "A mensagem do commit não pode ser vazia.",
                "The commit message cannot be empty.",
            ))

    def commit_local_changes(self) -> None:
        self.console.step(translate("Verificando alterações locais", "Checking local changes"))
        if not self.repository.has_local_changes():
            self.console.success(translate("Nenhuma alteração local", "No local changes"))
            return
        if not self.console.confirm(translate(
            "Deseja salvar todas as alterações agora?",
            "Save all changes now?",
        )):
            raise UserCancelled
        self.repository.stage_all()
        if not self.repository.has_staged_changes():
            self.console.warn(translate(
                "Nenhuma alteração pronta para commit.",
                "No changes ready to commit.",
            ))
            return
        self.repository.ensure_no_staged_conflict_markers()
        self.console.warn(translate("Resumo das alterações:", "Changes to commit:"))
        self.repository.staged_diff_stat()
        self.repository.commit(self.ask_commit_message())
        self.console.success(translate("Alterações salvas", "Changes committed"))

    def sync_with_remote(self, branch: str) -> None:
        self.console.step(translate(
            "Baixando atualizações do servidor", "Fetching updates from the server",
        ))
        self.repository.fetch(self.remote)
        if not self.repository.remote_has_updates(branch, self.remote):
            self.console.success(translate(
                "Seu repositório já está atualizado", "Your repository is up to date",
            ))
            return
        remote_branch: str = f"{self.remote}/{branch}"
        self.console.warn(translate(
            "Existem atualizações no servidor.", "Updates are available on the server.",
        ))
        if self.repository.merge_fast_forward(remote_branch):
            self.console.success(translate("Atualizações recebidas", "Updates received"))
            return
        self.console.warn(translate(
            "Fast-forward não foi possível. Tentando merge.",
            "Fast-forward was not possible. Trying merge.",
        ))
        if self.repository.merge(remote_branch):
            self.console.success(translate("Atualizações recebidas", "Updates received"))
            return
        conflicts: list[str] = self.repository.conflicted_files()
        if conflicts:
            self.show_unresolved_conflicts(conflicts)
            raise UserCancelled
        raise GitError(translate(
            "Erro ao atualizar repositório.", "Could not update the repository.",
        ))

    def push_changes(self, branch: str) -> None:
        self.console.step(translate(
            "Enviando alterações para o servidor", "Sending changes to the server",
        ))
        if not self.repository.has_commits_to_push():
            self.console.success(translate(
                "Nenhum commit novo para enviar", "No new commits to push",
            ))
            return
        self.repository.push(branch, self.remote)
        self.console.success(translate("Alterações enviadas", "Changes pushed"))

    def show_final_summary(self) -> None:
        self.console.step(translate("Resumo final", "Final summary"))
        self.console.write(translate("✓ alterações salvas", "✓ changes committed"))
        self.console.write(translate("✓ repositório atualizado", "✓ repository updated"))
        self.console.write(translate("✓ alterações enviadas", "✓ changes pushed"))
        self.console.write(translate(
            f"Log salvo em: {self.console.log_file}",
            f"Log saved to: {self.console.log_file}",
        ))

    def run(self) -> None:
        self.console.write(translate("SINCRONIZAÇÃO GIT", "GIT SYNC"))
        self.validate_environment()
        self.validate_remote()
        self.handle_pending_merge()
        self.setup_git_identity()
        branch: str = self.validate_branch()
        self.show_status()
        self.commit_local_changes()
        self.sync_with_remote(branch)
        self.push_changes(branch)
        self.show_final_summary()
        self.console.success(translate(
            "Sincronização concluída.", "Synchronization complete.",
        ))
