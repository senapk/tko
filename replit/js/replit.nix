{ pkgs }: {
	deps = [
    pkgs.python38Full
    pkgs.python38Packages.appdirs
    pkgs.nodejs-18_x
    pkgs.nodePackages.typescript-language-server
    pkgs.yarn
    pkgs.replitPackages.jest
	];
}

