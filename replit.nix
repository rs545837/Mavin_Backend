{ pkgs }: {
  deps = [
    pkgs.bash
    pkgs.python3
    pkgs.python3Packages.flask
    pkgs.texlive.combined.scheme-small
    pkgs.pandoc
    pkgs.noto-fonts
    pkgs.noto-fonts-cjk
    pkgs.noto-fonts-emoji
  ];
}