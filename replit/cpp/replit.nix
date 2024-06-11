{ pkgs }: {
	deps = [
    pkgs.python38Full
    pkgs.graphviz
    pkgs.clang_12
    pkgs.ccls
    pkgs.gdb
    pkgs.gnumake
	];
}
