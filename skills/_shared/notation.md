# Notation reference for AI papers

Usual readings of notation in machine-learning papers. Each paper defines its own
symbols, and a definition in the paper always wins over this file. Use the file to
know which readings are possible and where a symbol is ambiguous. Then find the
paper's own definition, or list the symbol as undefined.

Paper citations below refer to these versions: Attention Is All You Need
1706.03762v7, DeepSeek-V2 2405.04434v5, DeepSeek-V3 2412.19437v2, DeepSeek-V4
2606.19348v1, DeepSeekMath 2402.03300v3, DAPO 2503.14476v2, DPO 2305.18290v3,
MiniLLM 2306.08543v4, DDPM 2006.11239v2, Gated DeltaNet 2412.06464v3.

## Indices, labels and marks

- **Subscripts are usually indices.** $x_i$ can be coordinate $i$ of a vector or
  example $i$ of a dataset. $h_t$ is the vector for token $t$, called its _hidden
  state_.
- **Superscripts are often labels, not powers.** In $h_t^{(\ell)}$ the
  superscript in parentheses is usually a layer number. In DeepSeek-V2,
  $W^{DKV}$ and $k_t^C$ are labels. DeepSeek-V3's $\mathrm{FFN}^{(s)}_i$ and
  $\mathrm{FFN}^{(r)}_i$ mark shared and routed experts. $W^\top$ is a transpose
  and $x^2$ a square. Decide which reading applies before you compute anything.
- **Ranges.** $x_{1:T}$ means positions 1 through $T$, _including_ $T$, unlike a
  Python slice. $x_{<t}$ means every position before $t$. $X_{t,:}$ selects row
  $t$. Papers usually count from 1.

| Mark       | Usual reading                        | Known exception                                                                  |
| ---------- | ------------------------------------ | -------------------------------------------------------------------------------- |
| $\hat y$   | A prediction or an estimate          | DeepSeekMath's $\hat A_{i,t}$ is an estimated advantage                          |
| $\bar x$   | A mean                               | DDPM's $\bar\alpha_t=\prod_{s\le t}\alpha_s$ is a product, not a mean            |
| $\tilde x$ | A perturbed or unconstrained version | DeepSeek-V4's $\tilde B_l$ is a matrix before normalization                      |
| $x^\ast$   | The optimum                          | In DPO, $r^\ast$ is the true reward, which the method never observes             |
| $x'$       | A new value or an intermediate       | DeepSeek-V3's $g'_{i,t}$ is an expert weight before normalization                |
| $A^{-1}$   | The matrix inverse                   | It is not the entrywise reciprocal: $(A^{-1})_{ij}\ne1/A_{ij}$ in general        |

Symbols that have several jobs:

| Symbol         | Possible meanings                                                                        |
| -------------- | ---------------------------------------------------------------------------------------- |
| $\mid$         | Conditioning, as in $p(y\mid x)$; "such that" inside a set                               |
| $\vert x\vert$ | Absolute value; length of a sequence ($\vert o_i\vert$ tokens); number of set members    |
| $\Vert$        | Separates the arguments of a KL divergence, where order matters; $\Vert x\Vert$ is a norm |
| $\sim$         | "Is sampled from" in $x\sim p$; "roughly" in informal text                               |
| $T$            | Sequence length; softmax temperature; number of diffusion steps                          |
| $q$            | Attention query; a question (GRPO); student model $q_\theta$; encoder $q_\phi$ (ELBO)    |
| $\sigma$       | Sigmoid (DPO); standard deviation; in $\Sigma$, a covariance matrix                      |
| $\mathbf 1$    | Indicator $\mathbf 1[C]$; also $\mathbf 1_n$, a vector of $n$ ones                       |

## Relation signs

| Sign                 | Meaning                                                                                       |
| -------------------- | --------------------------------------------------------------------------------------------- |
| $=$                  | Two expressions are equal; a fitted law printed with $=$ is still an empirical fit            |
| $:=$, $\triangleq$   | "Is defined as": gives a name to an expression, such as a metric, a loss or a set             |
| $\in$                | "Belongs to": a shape ($Q\in\mathbb R^{n\times d}$) or a constraint ($B_l\in\mathcal M$)      |
| $\approx$            | An approximation, such as a sampled average standing in for an expectation                    |
| $\propto$            | Proportional to, with a normalizing constant left out: $p_i\propto e^{z_i}$                   |
| $\ll$                | Much smaller than, as in DeepSeek-V2's $d_c\ll d_hn_h$                                        |
| $\leftarrow$         | Assignment, as in an update rule                                                              |
| $\le$, $\ge$         | An inequality: a bound (the ELBO), a constraint ($A\ge0$), or a range ($0\le k\le n$)          |

The relation sign and the job of the whole line are different questions. Finding
$:=$ tells you that something is being named, not what kind of thing it is.

## Sums, products, counts

- $\sum_{i=1}^N x_i=x_1+\cdots+x_N$ and $\prod_{i=1}^N x_i=x_1\cdots x_N$. The index
  belongs to its operator, like a loop variable to its loop. In
  $y_i=\sum_j W_{ij}x_j$ the sum runs over $j$, and $i$ names an output entry. The
  free indices on the left-hand side give the output's shape.
- **The factor in front of a sum decides what gets equal weight.** For per-token
  terms $\ell_{it}$ of answer $i$:
  - $\frac1G\sum_i\frac1{\vert o_i\vert}\sum_t\ell_{it}$ weights each answer
    equally, so tokens of long answers get less weight (DeepSeekMath's GRPO).
  - $\frac1{\sum_i\vert o_i\vert}\sum_i\sum_t\ell_{it}$ weights each token equally
    (DAPO, §3.3).

  For answers of 2 and 8 tokens, the per-answer average gives each token weight
  1/4 or 1/16. The per-token average gives every token 1/10.
- **Indicator.** $\mathbf 1[C]$, also printed $\mathbb 1(C)$ or $\mathbb I(C)$,
  is 1 when condition $C$ holds and 0 otherwise. A sum of indicators counts how
  often the condition holds: $\sum_i\mathbf 1[\hat y_i=y_i]$ is the number of
  correct predictions. Check exactly which quantity the condition tests. In
  DeepSeek-V3, $f_i$ in equation (18), part of the balance loss (17), tests the
  raw score without the routing bias, so its count can differ from the experts
  that routing (16) selects.
- **Binomial coefficient.** $\binom nk=n!/(k!(n-k)!)$ counts the ways to choose
  $k$ of $n$ items when order does not matter; $\binom52=10$. $n!=1\cdots n$ and
  $0!=1$.
- **Intervals.** $[a,b]$ includes both ends and $(a,b)$ neither. Elsewhere $(a,b)$
  is a pair.

## Logarithms and exponentials

- ML papers mean the natural log unless they say otherwise; results are in nats,
  and base-2 logs give bits. $\log(ab)=\log a+\log b$ and
  $\log(a/b)=\log a-\log b$, but $\log(a+b)$ does not split. That is why papers
  work with log-probabilities: products become sums and ratios become
  differences (DPO and GRPO log-ratios).
- $-\log p\ge0$ for $p\le1$, and it grows without limit as $p\to0$.
- **Log-sum-exp.** $\log\sum_ie^{z_i}=m+\log\sum_ie^{z_i-m}$ with $m=\max_iz_i$.
  For $z=(1000,1001)$: $1001+\log(e^{-1}+1)\approx1001.313$. Softmax uses the same
  shift, and there it cancels in the division.
- **Softmax.** $\mathrm{softmax}(z)_j=e^{z_j}/\sum_{j'}e^{z_{j'}}$. The output is
  positive and sums to 1. Adding a constant to every input changes nothing. A
  large _spread_ between inputs saturates it: one weight near 1, the rest near 0,
  and the gradients become very small.

## Probability

- $p_\theta(y\mid x)$ is the probability that the model with parameters $\theta$
  gives output $y$ for input $x$. $p(y\mid x;\theta)$ is the same thing; the
  semicolon marks parameters, not a condition. $p_\theta(\cdot\mid x)$ is the
  whole distribution. RL papers write $\pi_\theta(o\mid q)$ and call the model a
  _policy_.
- $P(A\mid B)=P(A\cap B)/P(B)$ for $P(B)>0$. Swapping event and condition gives a
  different number: with 100 responses, 60 correct, 50 valid JSON and 40 both,
  $P(\text{correct}\mid\text{valid})=0.8$ but
  $P(\text{valid}\mid\text{correct})\approx0.67$.
- Independence: $P(A\cap B)=P(A)P(B)$. Bayes:
  $P(A\mid B)=P(B\mid A)P(A)/P(B)$.
- **Chain rule for text.**
  $\log p_\theta(y_{1:T}\mid x)=\sum_t\log p_\theta(y_t\mid x,y_{<t})$. This does
  not assume tokens are independent: every factor conditions on all earlier
  tokens. The usual loss is the negative of this sum divided by $T$. In training,
  $y_{<t}$ comes from the data; in generation, from the model's own earlier
  choices.

## Expectations and where samples come from

- $\mathbb E_{x\sim p}[f(x)]=\sum_xp(x)f(x)$, or $\int f(x)p(x)\,dx$ when $x$ has a
  density. Code estimates it with a batch mean,
  $\frac1N\sum_if(x_i)$ with $x_i\overset{\text{iid}}{\sim}p$: a _Monte Carlo
  estimate_.
- **The subscript says how the training data is produced.** The batch mean
  estimates the expectation only when the batch is drawn from that
  distribution.
  - DPO: $(x,y_w,y_l)\sim\mathcal D$, a fixed dataset collected and labeled
    before training. No fresh sampling during the step.
  - GRPO: $q\sim P(Q)$, then $\{o_i\}\sim\pi_{\theta_{old}}(O\mid q)$. A frozen
    copy of the model generates the answers, which are then scored.
  - On-policy distillation (MiniLLM, DeepSeek-V4): the student generates the text
    and a frozen teacher supplies probabilities for it. MiniLLM's actual sampler
    also mixes in teacher tokens.
- **Order of log and average matters.** $\mathbb E[\log X]\le\log\mathbb E[X]$
  for positive $X$ (Jensen). With probabilities 0.9 and 0.1:
  $\mathbb E[\log X]\approx-1.20$ but $\log\mathbb E[X]=\log0.5\approx-0.69$. In
  code: `np.log(p).mean()` and `np.log(p.mean())` are different losses.

## Densities, variance, error bars

- For discrete outcomes, $p(x)$ is a probability in $[0,1]$. For a continuous
  variable, $p(x)$ is a _density_: probability per unit, so
  $P(a\le X\le b)=\int_a^bp(x)\,dx$. A density can exceed 1 (uniform on
  $[0,0.5]$ has density 2), and its log can be positive. A single exact point has
  probability 0. Papers often use $p$ for both; check how the variable is
  modelled.
- $\mathrm{Var}(X)=\mathbb E[(X-\mu)^2]$; the standard deviation is its square
  root. $\mathcal N(\mu,\sigma^2)$ takes a variance, not a standard deviation.
  $\mathcal N(0,I)$ is a vector of independent standard normals.
- For independent variables, the mean of a product is the product of the means,
  and the variance of a sum is the sum of the variances. Two consequences: a
  product of two independent mean-0, variance-1 numbers has variance 1; and a
  dot product of two $d$-vectors with independent mean-0, variance-1 entries,
  a sum of $d$ such products, has variance $d$ (Attention Is All You Need,
  footnote 4).
- Standard error of a mean of $N$ independent runs is $\sigma/\sqrt N$. Before
  comparing $82.3\pm0.4$ with $81.5\pm0.4$, find out whether 0.4 is a standard
  deviation, a standard error or a confidence-interval half-width. With few runs,
  use a t multiplier rather than 1.96.

## Cross-entropy and KL divergence

- One observed outcome with predicted probability $q_i$ costs $-\log q_i$.
- $H(p,q)=-\sum_ip_i\log q_i$. With a one-hot label it is $-\log q_y$. PyTorch's
  `CrossEntropyLoss` takes logits, not probabilities.
- $H(p)=-\sum_ip_i\log p_i$ is the minimum of $H(p,q)$ over $q$; it is 0 only for
  a one-hot $p$.
- $D_{\mathrm{KL}}(p\Vert q)=\sum_ip_i\log(p_i/q_i)=H(p,q)-H(p)\ge0$, and it is 0
  only when $p=q$. **The order matters.** $D_{\mathrm{KL}}(p\Vert q)$ is infinite
  where $p_i>0=q_i$. $D_{\mathrm{KL}}(q\Vert p)$ is infinite where $q_i>0=p_i$.
  With target $p$, the first is the _forward_ KL and the second the _reverse_ KL.
  For $p=(0.9,0.1)$ and $q=(0.5,0.5)$ they are 0.37 and 0.51.
- Against a fixed teacher $p$, cross-entropy and $D_{\mathrm{KL}}(p\Vert q)$ give
  the student the same gradients. With the student first, they do not.

## Vectors and matrices

- $a\in\mathbb R^d$ is a vector of $d$ real numbers. $A\in\mathbb R^{m\times n}$
  has $m$ rows and $n$ columns, an array of shape `[m, n]`. Bold letters
  sometimes mark vectors; the definition decides.
- Conventions differ. Attention stacks tokens as the _rows_ of $Q$. MLA, Gated
  DeltaNet and LoRA write $Wh$ with column vectors. `nn.Linear` computes
  `x @ W.T` on rows.

| Expression        | Inputs                  | Result                                         |
| ----------------- | ----------------------- | ---------------------------------------------- |
| $a^\top b$        | two $d$-vectors         | one number, $\sum_ia_ib_i$                     |
| $ab^\top$         | $m$- and $n$-vectors    | $m\times n$ matrix with entries $a_ib_j$       |
| $AB$              | $m\times k$, $k\times n$ | $m\times n$; the shared $k$ is summed away     |
| $A\odot B$        | same shapes             | entrywise product, same shape                  |
| $[a;b]$           | $m$- and $n$-vectors    | concatenation; check the joining axis          |

- $(AB)C=A(BC)$, but $AB\ne BA$ in general. $(AB)^\top=B^\top A^\top$. Papers do
  not inherit NumPy broadcasting: adding a vector to a matrix needs a stated axis.
- $\Vert x\Vert_2=\sqrt{\sum x_i^2}$; $\Vert x\Vert_1=\sum\vert x_i\vert$;
  $\Vert A\Vert_2$ is the largest factor by which $A$ stretches a vector.
  $\mathrm{rank}(A)$ is the number of independent columns. $\vert\det A\vert$
  scales volume. $A\ge0$ means entrywise nonnegative, while $A\succeq0$ means
  positive semidefinite. $I$ is the identity.

## Gradients and optimization

- $\partial\mathcal L/\partial\theta_i$ is one number: the rate of change of the
  loss when only $\theta_i$ moves. $\nabla_\theta\mathcal L$ collects them into a
  vector. The subscript says what varies: $\nabla_x\log p(x)$ varies the
  _input_, and diffusion papers call it the _score_.
- Gradient descent: $\theta\leftarrow\theta-\eta\nabla_\theta\mathcal L$ with
  $\eta>0$.
- A Jacobian of $y=f(x)$ with $n$ inputs and $m$ outputs is $m\times n$, with
  entries $J_{ij}=\partial y_i/\partial x_j$.
- $\min_\theta f$ is a value; $\arg\min_\theta f$ is the parameters that reach
  it. An argmin states the goal and leaves the update algorithm open. MiniLLM
  states an argmin in equation (1), then derives and modifies the gradient it
  actually uses in equation (7).
- $\mathrm{sg}(x)$ (stop-gradient) passes $x$ forward but blocks gradients, like
  `.detach()`. Two expressions with the same value can train differently.

## Sets and constraints

- $\{\cdot\}$ is unordered with no repeats; $(\cdot)$ is an ordered tuple.
- $x\in A$ membership, $A\cup B$ union, $A\cap B$ intersection, $\vert A\vert$
  count, $\forall$ "for every", $\exists$ "there exists".
- Set-builder $\{x\in S\mid\text{cond}\}$ is the comprehension
  `{x for x in S if cond(x)}`; the bar means "such that". Some papers use a
  colon.
- A constraint says which values are allowed, not how to produce one. Look for
  the computation that produces a value satisfying it, for example a
  normalization or a projection.
- When samples are counted, count indices, not distinct texts: two identical
  answers are still two samples.

## Greek letters

| Letter                 | Name    | Common roles                                                         |
| ---------------------- | ------- | -------------------------------------------------------------------- |
| $\alpha$               | alpha   | mixing weight or scale; decay (Gated DeltaNet); noise schedule (DDPM) |
| $\beta$                | beta    | penalty strength (DPO, GRPO); writing strength (Gated DeltaNet); noise schedule (DDPM) |
| $\gamma$               | gamma   | RL discount; a step size (DeepSeek-V3 bias update)                   |
| $\delta,\Delta$        | delta   | a difference or change; $\Delta^{K-1}$ can name the simplex          |
| $\epsilon,\varepsilon$ | epsilon | noise (DDPM); clipping range (PPO/GRPO); small stabilizer            |
| $\eta$                 | eta     | learning rate                                                        |
| $\theta,\Theta$        | theta   | model parameters; RoPE rotation angles                               |
| $\lambda,\Lambda$      | lambda  | regularization weight; eigenvalue                                    |
| $\mu$                  | mu      | a mean; gradient steps per batch (DeepSeekMath Algorithm 1)          |
| $\pi,\Pi$              | pi      | a policy; $\prod$ is the product operator                            |
| $\rho$                 | rho     | a probability ratio; a correlation                                   |
| $\sigma,\Sigma$        | sigma   | sigmoid; standard deviation; covariance; $\sum$ is the sum operator  |
| $\tau$                 | tau     | temperature; threshold; RL trajectory                                |
| $\phi,\varphi,\Phi$    | phi     | parameters of a second network (encoder); features; an angle         |
| $\psi,\Psi$            | psi     | parameters of another network, such as a value model $V_\psi$        |
| $\omega,\Omega$        | omega   | frequency; $\Omega$ a complexity lower bound or a set of outcomes    |

Font variants such as $\phi/\varphi$ are usually the same letter, but a paper can
use both for different variables.

## Other equation families to recognize

- **Selective state-space models** (Mamba): $h_t=\bar A_th_{t-1}+\bar B_tx_t$,
  $y_t=C_th_t$. The bars mark parameters discretized from continuous time, not
  means. "Selective" means the parameters depend on the input.
- **SDEs:** $dX_t=f(X_t,t)\,dt+g(X_t,t)\,dW_t$. Euler–Maruyama replaces $dW_t$
  with Gaussian noise of variance $\Delta t$.
- **Change of variables:**
  $p_Y(y)=p_X(f^{-1}(y))\,\vert\det J_{f^{-1}}(y)\vert$. For $y=2x$,
  $p_Y(y)=p_X(y/2)/2$.
- **Min–max (GANs):** $\min_G\max_DV(D,G)$. Training alternates gradient steps
  rather than solving the inner max.
- **Probability simplex:**
  $\Delta^{K-1}=\{p\in\mathbb R^K\mid p_i\ge0,\sum_ip_i=1\}$; the superscript is
  a dimension, not a power.
- **Normalization:** $\hat x=(x-\mu)/\sqrt{\sigma^2+\epsilon}$. The equation does
  not say which entries feed $\mu$ and $\sigma^2$. Batch norm uses each feature
  across examples, layer norm each token across features.
- **Big-O:** $O(L^2d)$ describes growth up to a constant factor. Two methods with
  the same big-O can differ a lot in speed and memory traffic. Check which cost a
  paper measured (arithmetic, memory, KV-cache reads) and in which phase
  (prefill or decode).
