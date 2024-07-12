Tabby
======
Backup your Safari tab groups with Tabby.

Safari tab groups are an awesome way to manage your bookmarks. But, unfortunately at the moment, Safari does not provide a way to backup bookmarks stored within tab groups.

So let's fix that.

Tabby can:
- Export tab groups as HTML
- Export tab groups as CSV
- Export tab groups from default profile
- Export tab groups from all other profiles
- Export tab groups in current order (including tab order within groups)

## Getting started

### Install ruby
To use this tool, you will need to have a working ruby dev environment.

If you haven't installed ruby before, you can follow these directions:
https://gorails.com/setup/macos/14-sonoma#ruby

### Install script
1. `git clone git@github.com:mokolabs/tabby.git ~/Desktop/tabby`
2. Open your terminal app.
3. Run `cd ~/Desktop/tabby` to open the tabby directory.
4. Run `bundle install` to install dependencies.
5. Run `ruby tabby.rb` to export your tab groups to the desktop.

## Optional steps
- Need to customize the export location? Just pass a file path to the tabby command.
`ruby tabby.rb ~/Library/Backup`

- Need to move tabby to a different location? The script should work in any location within your home directory.

- Need to backup your tab groups on a daily basis? Just write a cron task that runs the tabby command!

## Feedback
Have a suggestion? Your feedback is welcome! Feel free to open an issue or PR.