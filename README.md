# latex-stats-uploader

GitHub Action for uploading stats about latex projects to a server.
Designed for use with my [thesis-tracker](https://github.com/georgejkaye/thesis-tracker) project.

## Usage

You can use GitHub actions [variables](https://docs.github.com/en/actions/learn-github-actions/variables) and [secrets](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions) to keep data in GitHub rather than hardcoding it into your action file.
Your password should definitely be kept in a secret!

```yml
- name: Upload stats to the server
  uses: georgejkaye/latex-stats-uploader@v1.0
  with:
    main: main.tex
    sha: ${{ github.sha }}
    datetime: ${{ github.event.head_commit.timestamp }}
    endpoint: ${{ vars.TRACKER_API }}
    user: ${{ vars.TRACKER_USER }}
    password: ${{ secrets.TRACKER_PASSWORD }}
```

### Parameters

#### `main`

The main file

#### `sha`

The sha to assign to this upload

#### `datetime`

The datetime to assign to this upload

#### `endpoint`

The endpoint the stats API is located at

#### `user`

User for the API

#### `password`

Password for the API

