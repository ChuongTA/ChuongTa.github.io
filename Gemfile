source 'https://rubygems.org'

# Depend on Jekyll directly rather than the "github-pages" meta-gem.
# github-pages exists only to mirror GitHub's legacy branch-based build
# whitelist; since the site is built and deployed via our own Actions
# workflow now, we don't need it, and its ~90-gem dependency tree was the
# likely cause of CI-only build failures. Pinned to the same Jekyll
# version github-pages was using, so behavior doesn't change.
gem 'jekyll', '~> 3.10.0'

group :jekyll_plugins do
  gem 'jekyll-feed'
  gem 'jekyll-sitemap'
  gem 'jekyll-redirect-from'
  gem 'jekyll-paginate'
  gem 'jekyll-gist'
  gem 'jemoji'
  gem 'webrick', '~> 1.8'
end

# _config.yml sets kramdown input: GFM, which github-pages used to pull in
# transitively — now needs to be explicit.
gem 'kramdown-parser-gfm'

# Required for Windows timezone resolution locally
gem "tzinfo-data", platforms: [:mingw, :mswin, :x64_mingw, :jruby]
