\LoadClass[a4paper,12pt]{report} % Classe du document

%--------------------- Packages ------------------------


\RequirePackage{titlesec} % For customizing chapter and section titles
\RequirePackage{tocloft} % For customizing the table of contents


\RequirePackage[french]{babel} % Langue du document
\RequirePackage[utf8]{inputenc} % Caractères spéciaux
\RequirePackage[section]{placeins} % Pour placement de section
\RequirePackage[T1]{fontenc} % Quelques lettres qui sont pas inclus dans UTF-8
\RequirePackage{mathtools} % Paquet pour des équations et symboles mathématiques
\RequirePackage{siunitx} % Pour écrire avec la notation scientifique (Ex.: \num{2e+9})
\RequirePackage{float} % Pour placement d'images
\RequirePackage{graphicx} % Paquet pour insérer des images
\RequirePackage[justification=centering]{caption} % Pour les légendes centralisées
\RequirePackage{subcaption}
\RequirePackage{wallpaper}
\RequirePackage{nomencl}
%\makenomenclature
\RequirePackage{fancyhdr}
\RequirePackage{fancybox}
\RequirePackage{url}
\RequirePackage[hidelinks]{hyperref}%Paquet pour insérer légendes dans des sous-figures comme Figure 1a, 1b
\RequirePackage[left=2.5cm,right=2.5cm,top=2cm,bottom=3.5cm]{geometry} % Configuration de la page

% Customize chapter titles to match book document class
\titleformat{\chapter}[display]
  {\normalfont\huge\bfseries}{\chaptertitlename\ \thechapter}{20pt}{\Huge}
\titlespacing*{\chapter}
  {0pt}{-10pt}{10pt}

  
% Customize section titles to match book document class
\titleformat{\section}
  {\normalfont\Large\bfseries}{\thesection}{1em}{}
%-------------------- Informations sur le rapport ----------------------

\newcommand{\UE}[1]{\renewcommand{\UE}{#1}}
\newcommand{\sujet}[1]{\renewcommand{\sujet}{#1}}
\newcommand{\titre}[1]{\renewcommand{\titre}{#1}}
\newcommand{\enseignant}[1]{\renewcommand{\enseignant}{#1}}
\newcommand{\eleves}[1]{\renewcommand{\eleves}{#1}}
\newcommand{\jury}[1]{\renewcommand{\jury}{#1}}


\newcommand{\fairemarges}{
    \fancyhf{} %Clear Everything.
    \fancyheadoffset{1cm}
    \setlength{\headheight}{1.5cm}
    \fancyfoot[C]{\thepage} %Page Number
    \renewcommand{\headrulewidth}{1pt} %0pt for no rule, 2pt thicker etc...
    \renewcommand{\footrulewidth}{1pt}
    \fancyfoot[L]{Rapport du Projet} % BOTTOM LEFT
    \fancyfoot[R]{2025-2026} % BOTTOM RIGHT
    \fancyhead[L]{\nouppercase{\leftmark}} % TOP LEFT
    \fancyhead[R]{} % TOP RIGHT
    \pagestyle{fancy}
}

\newcommand{\fairepagedegarde}{
\begin{titlepage}

\ThisLRCornerWallPaper{1}{logos/background.png}
	
    %\vspace{-2cm}
    %\includegraphics[width=0.2\textwidth]{logos/um5logo.png}
    %\hfill
    \centering %Centraliser le contenu
    %\hspace{-2cm}
    \includegraphics[width=0.3\textwidth]{logos/ensias.png}\hfill
	\includegraphics[width=0.3\textwidth]{logos/um5logo.png}\par\vspace{1cm} %Insertion du logo
	{\scshape\LARGE École Nationale Supérieure d'Informatique et d'Analyse des Systèmes - Rabat \par} %Nom de l'université
	\vspace{1.5cm}%Espace de 1,5cm
	{\scshape\Large \UE \par \sujet \par} %sous-titre
	\vspace{1cm}%Espace de 1cm
    \rule{\linewidth}{0.2 mm} \par \vspace{0.4cm}
	{\huge\bfseries \titre \par}
    \rule{\linewidth}{0.2 mm} \par \vspace{1.5cm}
	\vspace{1cm}%Espace de 3cm
    
	\begin{minipage}{0.5\textwidth} % Minipage pour faire deux colonnes
            \begin{flushleft} \large % Envoyer à gauche
            \textbf{Élèves :}\par % Pour le titre au dessus des noms à gauche
            \eleves\par % Remplacer pour chacun
            \end{flushleft}
        \end{minipage}
        ~
        \begin{minipage}{0.4\textwidth}
            \begin{flushright} \large
            \textbf{Enseignant :} \par
             \enseignant \par
            \end{flushright}
        \end{minipage}
        ~
        \par

        \vfill
        {\large Année Universitaire 2025-2026\par}

\end{titlepage}
}

\newcommand{\tabledematieres}{
\tableofcontents
\newpage
}

\newcommand{\insererfigure}[4]{

}



