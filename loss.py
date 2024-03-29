import torch as th
from torch import nn as nn
from torch.nn import functional as F

def ELBO(x, prior_mu, prior_std, enc_mu, enc_std, dec_mu, dec_std, device='cuda', nll_type='bernoulli'):

    resample = False

    kld_loss = _kld_gauss(enc_mu, enc_std, prior_mu, prior_std)

    if nll_type == 'bernoulli':
        nll_loss = th.sum(_nll_loss(x, params=dec_mu, nll_type=nll_type))

    loss = kld_loss + nll_loss

    return loss, kld_loss, nll_loss, resample

def IWAE(x, prior_mu, prior_std, enc_mu, enc_std, dec_mu, dec_std, n_samples, device='cuda', nll_type='bernoulli'):

    resample = False

    nll_loss = _nll_loss(x=x.repeat(n_samples, 1), params=dec_mu, nll_type=nll_type) # batch * n_samples
    kld_loss = _kld_gauss(enc_mu, enc_std, prior_mu, prior_std) # batch * 1

    log_weight = (nll_loss + kld_loss) # batch * n_samples
    weight = F.softmax(log_weight)

    loss = th.sum(weight * log_weight, dim=0)

    return loss, kld_loss, th.sum(weight*nll_loss), resample


def FIVO(x, prior_mu, prior_std, enc_mu, enc_std, dec_mu, dec_std, n_samples, device='cuda', nll_type='bernoulli'):


    resample = False

    nll_loss = _nll_loss(x=x.repeat(n_samples, 1), params=dec_mu, nll_type=nll_type)  # batch * n_samples
    kld_loss = _kld_gauss(enc_mu, enc_std, prior_mu, prior_std)  # batch * 1

    log_weight = (nll_loss + kld_loss)  # batch * n_samples
    weight = F.softmax(log_weight)

    loss = th.sum(weight * log_weight, dim=0)

    ESS = 1/th.sum(weight**2)

    if ESS < n_samples/2:
        resample = True

    return loss, kld_loss, th.sum(weight * nll_loss), resample





def _kld_gauss(mu1, std1, mu2, std2):

    KL_div = (2*th.log(std2) - 2* th.log(std1) + (std1.pow(2) + (mu1 - mu2).pow(2))/ std2.pow(2)-1)

    return 0.5* th.sum(KL_div)


def _nll_loss(x, params, nll_type):

    """
    :param x:
    :param params: if bernoulli, params represent "theta" which is list with length 1
                    if gauss, params represent "mu, sigma" which is list with length 2
    :param nll_type: Bernoulli or Gauss
    :return: nll_loss
    """

    if nll_type == "bernoulli":

        return th.mean(-x*th.log(params) - (1-x)*th.log(1-params), dim=1)

    elif nll_type == "gauss":

        return NotImplementedError
