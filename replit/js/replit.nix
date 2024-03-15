{ pkgs }: {
	deps = [
    pkgs.python38Full
    pkgs.nodejs-18_x
    pkgs.nodePackages.typescript-language-server
    pkgs.yarn
    pkgs.replitPackages.jest
	];
}

