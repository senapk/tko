{ pkgs }: {
	deps = [
    pkgs.python310Full
    pkgs.graphviz
    pkgs.clang_12
    pkgs.ccls
    pkgs.gdb
    pkgs.gnumake
	];
}
