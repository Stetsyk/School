Yes. Git can switch identity by folder with an  includeIf  rule in  ~/.gitconfig . Repos inside  School  would use your Stetsyk
 identity, and everything else keeps the work one.

 What I found

   • Your global  ~/.gitconfig  has the work identity ( ostetsyk  /  ostetsyk@zscaler.com ) and signs every commit with a work GPG
   key ( commit.gpgsign=true ).
   • It also turns  https://github.com/  URLs into SSH, so pushes authenticate with your SSH key. That key is presumably tied to
   the work GitHub account.
   •  School  is not a git repo yet, so you'd run  git init  there.

 So switching name and email isn't enough. The folder also needs its own SSH key for pushing to  Stetsyk , and work-key signing
 turned off there.

 Setup

 1. Add this to the end of  ~/.gitconfig :


 
   [includeIf "gitdir:~/Library/Mobile Documents/iCloud~md~obsidian/Documents/School/"]
       path = ~/.gitconfig-stetsyk
 

 2. Create  ~/.gitconfig-stetsyk :


 
   [user]
       name = Oleksii Stetsyk
       email = <your personal / GitHub noreply email>
   [commit]
       gpgsign = false
   [core]
       sshCommand = ssh -i ~/.ssh/id_ed25519_stetsyk -o IdentitiesOnly=yes
 

 3. Create an SSH key for the personal account and add the  .pub  file at github.com → Settings → SSH keys while logged in as
 Stetsyk:


 
   ssh-keygen -t ed25519 -C "Stetsyk" -f ~/.ssh/id_ed25519_stetsyk
 

 4. Initialize the repo and check it:


 
   cd "/Users/ostetsyk/Library/Mobile Documents/iCloud~md~obsidian/Documents/School"
   git init
   git config user.email                                 # should show the personal email
   git remote add origin git@github.com:Stetsyk/<repo>.git
 

 The trailing  /  in the  gitdir:  path makes the rule cover subfolders too. Repos anywhere else are unaffected. Any AI agent
 committing in that folder (Claude, Devin, OpenCode) would also use the Stetsyk identity automatically.

 Warning: git inside iCloud

 This folder is synced by iCloud Drive. iCloud doesn't handle  .git  folders well: it can create conflict copies like  index 2 ,
 sync files only partly, or offload objects. That can corrupt the repo, especially if you use more than one Mac. Some options:

   • Keep it and accept the risk. It's mostly fine with a single Mac, and GitHub acts as your backup.
   • Move the git data outside iCloud. Put the  .git  folder in  ~/git/School.git  and leave the notes where they are ( git init --
   separate-git-dir ~/git/School.git ). In that case the  includeIf  should use  gitdir:~/git/School.git , because it matches where
    .git  lives.
   • Use git sync instead of iCloud sync. Move the vault out of iCloud and sync it with git, for example with the Obsidian Git
   plugin.

 Optional:  gh  CLI

  gh  doesn't use git's per-folder config. If you use it, add the second account with  gh auth login  and switch with  gh auth swit
 ch .

 I can set this up for you. I'd need:

   1. The email to use for Stetsyk. GitHub's noreply address works if you'd rather not expose a personal one.
   2. Whether you already have an SSH key for that account or I should generate one.
   3. Which iCloud option you want.

 ✱ Did you know
   Set "show_hints": false in your config to hide these tips