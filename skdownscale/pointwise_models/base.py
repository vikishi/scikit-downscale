import warnings

import pandas as pd
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.utils import check_array, check_X_y
from sklearn.utils.validation import check_is_fitted


class TimeSynchronousDownscaler(BaseEstimator):
    def _check_X_y(self, X, y, **kwargs):
        if isinstance(X, pd.DataFrame) and isinstance(X, pd.DataFrame):
            assert X.index.equals(y.index)
            check_X_y(X, y)  # this may be inefficient
        else:
            X, y = check_X_y(X, y)
            warnings.warn('X and y do not have pandas DateTimeIndexes, making one up...')
            index = pd.date_range(periods=len(X), start='1950', freq='MS')
            X = pd.DataFrame(X, index=index)
            y = pd.DataFrame(y, index=index)
        return X, y

    def _check_array(self, array, **kwargs):
        if isinstance(array, pd.DataFrame):
            check_array(array)
        else:
            array = check_array(array)
            warnings.warn('array does not have a pandas DateTimeIndex, making one up...')
            index = pd.date_range(periods=len(array), start='1950', freq=self._timestep)
            array = pd.DataFrame(array, index=index)

        return array

    def _validate_data(self, X, y=None, reset=True, validate_separately=False, **check_params):
        """Validate input data and set or check the `n_features_in_` attribute.

        Parameters
        ----------
        X : {array-like, sparse matrix, dataframe} of shape \
                (n_samples, n_features)
            The input samples.
        y : array-like of shape (n_samples,), default=None
            The targets. If None, `check_array` is called on `X` and
            `check_X_y` is called otherwise.
        reset : bool, default=True
            Whether to reset the `n_features_in_` attribute.
            If False, the input will be checked for consistency with data
            provided when reset was last True.
        validate_separately : False or tuple of dicts, default=False
            Only used if y is not None.
            If False, call validate_X_y(). Else, it must be a tuple of kwargs
            to be used for calling check_array() on X and y respectively.
        **check_params : kwargs
            Parameters passed to :func:`sklearn.utils.check_array` or
            :func:`sklearn.utils.check_X_y`. Ignored if validate_separately
            is not False.

        Returns
        -------
        out : {ndarray, sparse matrix} or tuple of these
            The validated input. A tuple is returned if `y` is not None.
        """

        if y is None:
            if self._get_tags()['requires_y']:
                raise ValueError(
                    f'This {self.__class__.__name__} estimator '
                    f'requires y to be passed, but the target y is None.'
                )
            X = self._check_array(X, **check_params)
            out = X
        else:
            if validate_separately:
                # We need this because some estimators validate X and y
                # separately, and in general, separately calling check_array()
                # on X and y isn't equivalent to just calling check_X_y()
                # :(
                check_X_params, check_y_params = validate_separately
                X = self._check_array(X, **check_X_params)
                y = self._check_array(y, **check_y_params)
            else:
                X, y = self._check_X_y(X, y, **check_params)
            out = X, y

        # TO-DO: add check_n_features attribute
        if check_params.get('ensure_2d', True):
            self._check_n_features(X, reset=reset)

        return out
