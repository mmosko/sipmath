import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from .support import newtons_method_metalog, pdfMetalog_density


# TODO have to add summary function

def summary(m):
    print(' -----------------------------------------------\n',
          'Summary of Metalog Distribution Object\n',
          '-----------------------------------------------\n',
          '\nParameters\n',
          'Term Limit: ', m.output_list['params']['term_limit'], '\n',
          'Term Lower Bound: ', m.output_list['params']['term_lower_bound'], '\n',
          'Boundedness: ', m.output_list['params']['boundedness'], '\n',
          'Bounds (only used based on boundedness): ', m.output_list['params']['bounds'], '\n',
          'Step Length for Distribution Summary: ', m.output_list['params']['step_len'], '\n',
          'Method Use for Fitting: ', m.output_list['params']['fit_method'], '\n',
          '\n\n Validation and Fit Method'
          )
    print(m.output_list['Validation'].to_string(index=False))


def rmetalog(m, n=1, term=2, generator='rand'):
    m = m.output_list
    # Input validation
    valid_terms = np.asarray(m['Validation']['term'])
    valid_terms_printout = " ".join(str(t) for t in valid_terms)
    if (type(n) != int) or (n < 1) or ((n % 1) != 0):
        raise TypeError('Error: n must be a positive numeric interger')

    if (type(term) != int) or (term < 2) or ((term % 1) != 0) or not (term in valid_terms):
        raise TypeError('Error: term must be a single positive numeric interger contained '
                        'in the metalog object. Available terms are: ' + valid_terms_printout)

    if generator == 'hdr':
        x_arr = np.arange(1, n + 1)
        v_index = np.random.randint(80000)

        def hdrgen(pm_index):
            return (np.mod(((np.mod((v_index + 1000000) ^ 2 + (v_index + 1000000) * (pm_index + 10000000), 99999989)) +
                            1000007) * ((np.mod((pm_index + 10000000) ^ 2 + (pm_index + 10000000) *
                                                (np.mod((v_index + 1000000) ^ 2 + (v_index + 1000000) *
                                                        (pm_index + 10000000), 99999989)), 99999989)) + 1000013),
                           2147483647) + 0.5) / 2147483647

        vhdrgen = np.vectorize(hdrgen)

        x = vhdrgen(x_arr)
    else:
        x = np.random.rand(n)

    Y = pd.DataFrame(np.array([np.repeat(1, n)]).T, columns=['y1'])

    # Construct initial Y Matrix values
    Y['y2'] = np.log(x / (1 - x))

    if (term > 2):
        Y['y3'] = (x - 0.5) * Y['y2']

    if (term > 3):
        Y['y4'] = x - 0.5

    # Complete the values through the term limit
    if (term > 4):
        for i in range(5, (term + 1)):
            y = "".join(['y', str(i)])
            if (i % 2 != 0):
                Y[y] = Y['y4'] ** (i // 2)

            if (i % 2 == 0):
                z = "".join(['y', str(i - 1)])
                Y[y] = Y['y2'] * Y[z]

    amat = "".join(['a', str(term)])
    a = m['A'][amat].iloc[0:(term)].to_frame()
    s = np.dot(Y, a)

    if (m['params']['boundedness'] == 'sl'):
        s = m['params']['bounds'][0] + np.exp(s)

    if (m['params']['boundedness'] == 'su'):
        s = m['params']['bounds'][1] - np.exp(-(s))

    if (m['params']['boundedness'] == 'b'):
        s = (m['params']['bounds'][0] + (m['params']['bounds'][1]) * np.exp(s)) / (1 + np.exp(s))

    return (s)


def dmetalog(m, q, term=3):
    valid_terms = np.asarray(m.output_list['Validation']['term'])

    if (term not in valid_terms) or type(term) != int:
        raise TypeError(
            'Error: term must be a single positive numeric interger contained in the metalog object. Available '
            'terms are: ' + ' '.join(map(str, valid_terms)))

    qs = list(map(lambda qi: newtons_method_metalog(q=qi, m=m, term=term), q))
    ds = list(map(lambda yi: pdfMetalog_density(y=yi, m=m, t=term), qs))

    return (ds)


def pmetalog(m, q, term=3):
    valid_terms = np.asarray(m.output_list['Validation']['term'])

    if type(q) != list:
        raise TypeError('Error: q must be a list of numeric values')

    if not isinstance(q, (int, float, complex)) and not all(isinstance(x, (int, float, complex)) for x in q):
        raise TypeError('Error: all elements in q must be numeric')

    if (term in valid_terms) != True or type(term) != int:
        raise TypeError(
            'Error: term must be a single positive numeric interger contained in the metalog object. Available '
            'terms are: ' + ' '.join(map(str, valid_terms)))

    qs = list(map(lambda qi: newtons_method_metalog(q=qi, m=m, term=term), q))
    return (qs)


def qmetalog(m, y, term=3):
    # Input validation

    m = m.output_list
    valid_terms = np.asarray(m['Validation']['term'])
    valid_terms_printout = " ".join(str(t) for t in valid_terms)

    if type(y) != list:
        raise TypeError('Error: y must be a list of numeric values')

    y = np.asarray(y)
    if (all(isinstance(x, (int, float, complex)) for x in y)) != True or (max(y) >= 1) or (min(y) <= 0):
        raise TypeError('Error: y or all elements in y must be positive numeric values between 0 and 1')

    if (type(term) != int) or (term < 2) or ((term % 1) != 0) or (term in valid_terms) != True:
        print('smoo')
    if (type(term) != int) or (term < 2) or ((term % 1) != 0) or (term in valid_terms) != True:
        raise TypeError('Error: term must be a single positive numeric integer contained '
                        'in the metalog object. Available terms are: ' + valid_terms_printout)

    Y = pd.DataFrame(np.array([np.repeat(1, len(y))]).T, columns=['y1'])

    # Construct the Y Matrix initial values
    Y['y2'] = np.log(y / (1 - y))

    if (term > 2):
        Y['y3'] = (y - 0.5) * Y['y2']

    if (term > 3):
        Y['y4'] = y - 0.5

    # Complete the values through the term limit
    if (term > 4):
        for i in range(5, (term + 1)):
            y = "".join(['y', str(i)])
            if (i % 2 != 0):
                Y[y] = Y['y4'] ** (i // 2)

            if (i % 2 == 0):
                z = "".join(['y', str(i - 1)])
                Y[y] = Y['y2'] * Y[z]

    amat = "".join(['a', str(term)])
    a = m['A'][amat].iloc[0:(term)].to_frame()
    s = np.dot(Y, a)

    if (m['params']['boundedness'] == 'sl'):
        s = m['params']['bounds'][0] + np.exp(s)

    if (m['params']['boundedness'] == 'su'):
        s = m['params']['bounds'][1] - np.exp(-(s))

    if (m['params']['boundedness'] == 'b'):
        s = (m['params']['bounds'][0] + (m['params']['bounds'][1]) * np.exp(s)) / (1 + np.exp(s))

    s = s.flatten()
    return (s)


def plot(x):
    x = x.output_list
    # build plots
    InitalResults = pd.DataFrame(data={
        'term': (np.repeat((str(x['params']['term_lower_bound']) + ' Terms'), len(x['M'].iloc[:, 0]))),
        'pdfValues': x['M'].iloc[:, 0],
        'quantileValues': x['M'].iloc[:, 1],
        'cumValue': x['M']['y']})

    if len(x['M'].columns) > 3:
        for i in range(2, ((len(x['M'].iloc[0, :]) - 1) // 2 + 1)):
            TempResults = pd.DataFrame(data={
                'term': np.repeat((str(x['params']['term_lower_bound'] + (i - 1)) + ' Terms'), len(x['M'].iloc[:, 0])),
                'pdfValues': x['M'].iloc[:, (i * 2 - 2)],
                'quantileValues': x['M'].iloc[:, (i * 2 - 1)],
                'cumValue': x['M']['y']
            })

            InitalResults = InitalResults.append(pd.DataFrame(data=TempResults), ignore_index=True)

    # PDF plot
    sns.set()
    ymin = np.min(InitalResults['pdfValues'])
    ymax = np.max(InitalResults['pdfValues'])
    nterms = InitalResults.term.nunique()

    nrow = (nterms + 3) // 4

    if nterms < 4:
        ncol = nterms
    else:
        ncol = 4

    pdf_fig, axes = plt.subplots(nrow, ncol, sharey='col', squeeze=False)

    for t in range(nterms):
        data = InitalResults[(InitalResults['term'] == (InitalResults.term.unique()[t]))]
        x = data['quantileValues']
        y = data['pdfValues']
        r = t // 4
        c = t % 4
        axes[r, c].plot(x, y)
        axes[r, c].set_ylim(ymin, ymax * 1.1)
        axes[r, c].set_title(InitalResults.term.unique()[t])
        axes[r, c].tick_params(axis='both', which='major', labelsize=10)
        axes[r, c].tick_params(axis='both', which='minor', labelsize=10)

    for t in range(nterms, nrow * ncol):
        r = t // 4
        c = t % 4
        axes[r, c].axis('off')

    pdf_fig.text(0.5, 0.04, 'Quantile Values', ha='center')
    pdf_fig.text(0.04, 0.5, 'PDF Values', va='center', rotation='vertical')

    plt.yscale('linear')
    plt.tight_layout(rect=[0.05, 0.05, 1, 1])

    # Quantile Plot
    ymin = np.min(InitalResults['cumValue'])
    ymax = np.max(InitalResults['cumValue'])
    nterms = InitalResults.term.nunique()

    nrow = (nterms + 3) // 4

    if nterms < 4:
        ncol = nterms
    else:
        ncol = 4

    cdf_fig, axes = plt.subplots(nrow, ncol, sharey='col', squeeze=False)

    for t in range(nterms):
        data = InitalResults[(InitalResults['term'] == (InitalResults.term.unique()[t]))]
        x = data['quantileValues']
        y = data['cumValue']
        r = t // 4
        c = t % 4
        axes[r, c].plot(x, y)
        axes[r, c].set_ylim(ymin, ymax * 1.1)
        axes[r, c].set_title(InitalResults.term.unique()[t])
        axes[r, c].tick_params(axis='both', which='major', labelsize=10)
        axes[r, c].tick_params(axis='both', which='minor', labelsize=10)

    for t in range(nterms, nrow * ncol):
        r = t // 4
        c = t % 4
        axes[r, c].axis('off')

    cdf_fig.text(0.5, 0.04, 'Quantile Values', ha='center')
    cdf_fig.text(0.04, 0.5, 'CDF Values', va='center', rotation='vertical')

    plt.yscale('linear')
    plt.tight_layout(rect=[0.05, 0.05, 1, 1])

    return {'pdf': pdf_fig, 'cdf': cdf_fig}
