
def _to_dense(X):
    from scipy import sparse as sp
    return X.toarray() if sp.issparse(X) else X
