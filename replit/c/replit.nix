{ pkgs }: {
	deps = [
        pkgs.python38Full
        pkgs.python38Packages.appdirs
		pkgs.clang_12
		pkgs.ccls
		pkgs.gdb
		pkgs.gnumake
	];
}
