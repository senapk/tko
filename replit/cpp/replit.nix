{ pkgs }: {
	deps = [
    pkgs.python38Full
		pkgs.clang_12
		pkgs.ccls
		pkgs.gdb
		pkgs.gnumake
	];
}
