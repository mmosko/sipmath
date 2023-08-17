import pandas as pd
import numpy as np

def MLprobs(x_old, step_len):
    l = len(x_old)
    x = pd.DataFrame()
    x['x'] = x_old

    x.sort_values(by='x')

    x['probs'] = 0
    for i in range(0,l):
            if i == 0:
                x.loc[i,'probs'] = .5/l
            else:
                x.loc[i, 'probs'] = x.loc[i-1, 'probs'] + 1/l


    if len(x.index) > 100:
        num = int(((1 - step_len) / step_len))
        y2 = np.linspace(step_len, 1 - step_len, num)

        tailstep = step_len / 10

        y1 = np.linspace(tailstep, (min(y2) - tailstep), ((min(y2) - tailstep) / tailstep))

        y3 = np.linspace((max(y2) + tailstep), (max(y2) + tailstep * 9), ((tailstep * 9) / tailstep))

        y = np.hstack((y1, y2, y3))

        x_new = np.quantile(x_old, y)

        df_x = {}

        df_x['x'] = x_new

        df_x['probs'] = y

    return df_x


def pdfMetalog(a, y, t, bounds = [], boundedness = 'u'):
    d = y * (1 - y)
    f = y - .5
    l = np.log(y / (1 - y))

    # Initiate pdf

    # For the first three terms
    x = a[1]/d

    if a[2] != 0:
        x = x + a[2] * ((f / d) + l)

    # For the fourth term
    if t > 3:
        x = x + a[3]

    # Initalize some counting variables
    e = 1
    o = 1

    # For all other terms greater than 4
    if (t > 4):
        for i in range(5,t+1):
            if (i % 2) != 0:
                # iff odd
                x = x + ((o + 1) * a[i-1] * f ** o)
                o = o + 1

            if (i % 2) == 0:
                # iff even
                x = x + a[i-1] * (((f ** (e + 1)) / d) + (e + 1) * (f ** e) * l)
                e = e + 1


    # Some change of variables here for boundedness
    x = x**(-1)

    if boundedness != 'u':
        M = quantileMetalog(a, y, t, bounds = bounds, boundedness = 'u')

    if boundedness == 'sl':
        x = x * np.exp(-M)

    if boundedness == 'su':
        x = x * np.exp(M)

    if boundedness == 'b':
        x = (x * (1 + np.exp(M)) ** 2) / ((bounds[1] - bounds[0]) * np.exp(M))

    return x



def quantileMetalog(a, y, t, bounds = [], boundedness = 'u'):
    # Some values for calculation
    f = y - 0.5
    l = np.log(y / (1 - y))

    # For the first three terms
    x = a[0] + a[1] * l + a[2] * f * l

    # For the fourth term
    if t > 3:
        x = x + a[3] * f

    # Some tracking variables
    o = 2
    e = 2

    # For all other terms greater than 4
    if t > 4:
        for i in range(5,t+1):
            if (i % 2) == 0:
                x = x + a[i-1] * f ** e * l
                e = e + 1

            if (i % 2) != 0:
                x = x + a[i-1] * f ** o
                o = o + 1

    if boundedness == 'sl':
        x = bounds[0] + np.exp(x)

    if boundedness == 'su':
        x = bounds[1] - np.exp(-x)

    if boundedness == 'b':
        x = (bounds[0] + bounds[1] * np.exp(x)) / (1 + np.exp(x))

    return x


def diffMatMetalog(term_limit, step_len):
    y = np.arange(step_len, 1, step_len)
    Diff = np.array([])

    for i in range(0, (len(y))):
        d = y[i] * (1 - y[i])
        f = (y[i] - 0.5)
        l = np.log(y[i] / (1 - y[i]))

        # Initiate pdf
        diffVector = 0

        # For the first three terms
        x = (1 / d)
        diffVector = [diffVector, x]

        if term_limit > 2:
            diffVector.append((f / d) + l)


        # For the fourth term
        if term_limit > 3:
            diffVector.append(1)

        # Initalize some counting variables
        e = 1
        o = 1

        # For all other terms greater than 4
        if term_limit > 4:
            for i in range(5,(term_limit+1)):
                if (i % 2) != 0:
                # iff odd
                    diffVector.append((o + 1) * f ** o)
                    o = o + 1


                if (i % 2) == 0:
                # iff even
                    diffVector.append(((f ** (e + 1)) / d) + (e + 1) * (f ** e) * l)
                    e = e + 1
        if np.size(Diff) == 0:
            Diff = diffVector
        else:
            Diff = np.vstack((Diff, diffVector))


    Diff_neg = -1*(Diff)
    new_Diff = np.hstack((Diff[:,[0]], Diff_neg[:,[0]]))

    for c in range(1,(len(Diff[1,:]))):
        new_Diff = np.hstack((new_Diff, Diff[:,[c]]))
        new_Diff = np.hstack((new_Diff, Diff_neg[:,[c]]))

    new_Diff = pd.DataFrame(data=new_Diff)


    return new_Diff

def newtons_method_metalog(m,q,term):
  #a simple newtons method application
  m = m.output_list
  alpha_step = 0.01
  err = 0.0000001
  temp_err = 0.1
  y_now = 0.5
  avec = 'a'+str(term)
  a = m['A'][avec]

  i = 1
  while(temp_err>err):
    frist_function = (quantileMetalog(a,y_now,term,m['params']['bounds'],m['params']['boundedness'])-q)
    derv_function = pdfMetalog(a,y_now,term,m['params']['bounds'],m['params']['boundedness'])
    y_next = y_now-alpha_step*(frist_function*derv_function)
    temp_err = abs((y_next-y_now))
    if y_next > 1:
      y_next = 0.99999

    if y_next < 0:
      y_next = 0.000001

    y_now = y_next
    i = i+1

    if i > 10000:
      raise StopIteration('Approximation taking too long, quantile value: '+str(q)+' is to far from distribution median. Try plot() to see distribution.')

  return(y_now)

def pdfMetalog_density(m,t,y):
  m = m.output_list
  avec = 'a' + str(t)
  a = m['A'][avec]
  bounds = m['params']['bounds']
  boundedness = m['params']['boundedness']

  d = y * (1 - y)
  f = (y - 0.5)
  l = np.log(y / (1 - y))

  # Initiate pdf

  # For the first three terms
  x = (a[1] / d)
  if (a[2] != 0):
    x = x + a[2] * ((f / d) + l)

  # For the fourth term
  if (t > 3):
    x = x + a[3]

  # Initalize some counting variables
  e = 1
  o = 1

  # For all other terms greater than 4
  if (t > 4):
    for i in range(5,t+1):
      if (i % 2) != 0:
        # iff odd
        x = x + ((o + 1) * a[i-1] * f**o)
        o = o + 1


      if (i % 2) == 0:
        # iff even
        x = x + a[i-1] * (((f**(e + 1)) / d) + (e + 1) * (f**e) * l)
        e = e + 1




  # Some change of variables here for boundedness

  x = (x**(-1))

  if (boundedness != 'u'):
    M = quantileMetalog(a, y, t, bounds = bounds, boundedness = 'u')

  if (boundedness == 'sl'):
    x = x * np.exp(-M)

  if (boundedness == 'su'):
    x = x * np.exp(M)

  if (boundedness == 'b'):
    x = (x * (1 + np.exp(M))**2) / ((bounds[1] - bounds[0]) * np.exp(M))

  return(x)