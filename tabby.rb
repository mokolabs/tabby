require "csv"
require "fileutils"
require "htmlbeautifier"
require "markaby"
require "sqlite3"
require "tempfile"

# Copy safari tabs into temporary file
base = File.expand_path(ARGV.length == 1 ? ARGV[0] : "~/Desktop")
base = File.join(base, "tabgroups"); FileUtils.mkdir_p(base)
library = "~/Library/Containers/com.apple.Safari/Data/Library/Safari"
original = File.expand_path("#{library}/SafariTabs.db")
temporary = Tempfile.new("SafariTabs.db"); FileUtils.cp(original, temporary.path)

# Export bookmarks
begin
  db = SQLite3::Database.open(temporary.path)

  puts db
  # Select tab groups from personal profile
  personal = [:personal, "SELECT id, title FROM bookmarks WHERE type = 1 AND parent = 0 AND subtype == 0 AND num_children > 0 AND hidden == 0 ORDER BY id DESC"]

  # Select tab groups from all other profiles
  profiles = "SELECT id, title FROM bookmarks WHERE subtype = '2' and title != ''"
  profiles = db.execute(profiles).map do |profile|
    [profile[1].downcase.to_sym, "SELECT id, title FROM bookmarks WHERE parent = #{profile[0]} AND subtype == 0 AND num_children > 0 ORDER BY id DESC"]
  end

  # Export bookmarks to CSV and HTML
  [personal, profiles.flatten].each do |profile|
    profile, query = profile
    tab_groups = db.execute(query)

    profile_directory = File.join(base, profile.to_s)
    FileUtils.mkdir_p(profile_directory)

    # Export to CSV
    CSV.open("#{profile_directory}/bookmarks.csv", "w") do |csv|
      csv << ["Tab Group", "Bookmark", "URL"]

      tab_groups.each do |group|
        id, group = group

        query = "SELECT title, url FROM bookmarks WHERE parent = #{id} AND title NOT IN ('TopScopedBookmarkList', 'Untitled', 'Start Page') ORDER BY order_index ASC"
        bookmarks = db.execute(query)

        bookmarks.each do |bookmark|
          name, url = bookmark
          csv << [group, name, url]
        end
      end
    end

    # Export to HTML
    File.open("#{profile_directory}/bookmarks.html", "w") do |html|
      mab = Markaby::Builder.new
      mab.html do
        head do
          title "#{profile.capitalize} Bookmarks"
          meta charset: "UTF-8"
        end
        body do
          h1 "#{profile.capitalize} Bookmarks"

          tab_groups.each do |group|
            id, name = group

            query = "SELECT title, url FROM bookmarks WHERE parent = #{id} AND title NOT IN ('TopScopedBookmarkList', 'Untitled', 'Start Page') ORDER BY order_index ASC"
            bookmarks = db.execute(query)

            h3 name
            ul do
              bookmarks.each do |bookmark|
                name, url = bookmark
                li { a name, href: url }
              end
            end
          end
        end
      end

      html.puts HtmlBeautifier.beautify(mab.to_s, tab_width: 2)
    end
  end

  db.close
ensure
  # Delete temporary file
  temporary.close
  temporary.unlink
end