find -maxdepth 1 ! -name .git ! -name .nojekyll ! -name sync.sh -exec rm -rv {} \;
cp -r ../../swmm-python/swmm-pandas/docs/_build/html/* .