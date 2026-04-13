# Two-line test (Simonsohn 2018, app v0.52, last update 2018-11-23)
# Source: Uri Simonsohn (urisohn@gmail.com)
# https://webstimate.org/twolines/
# Packages required: mgcv, sandwich, lmtest

# Function 1 — reformat p-value for printing on chart
rp <- function(p) {
  if (p < .0001) return("p<.0001") else return(paste0("p=", sub("^(-?)0.", "\\1.", sprintf("%.4f", p))))
}

# Function 2 — evaluate a string as an expression
eval2 <- function(string) eval(parse(text = string))

# Function 3 — interrupted regression at a given breakpoint xc
reg2 <- function(f, xc, graph = 1, family = "gaussian") {

  # (1) Extract variable names from formula
  y.f       <- all.vars(f)[1]
  x.f       <- all.vars(f)[2]
  var.count <- length(all.vars(f))
  if (var.count > 2) nox.f <- drop.terms(terms(f), dropx = 1, keep.response = TRUE)

  xu <- eval2(x.f)
  yu <- eval2(y.f)

  unique.x <- length(unique(xu))
  sx.f     <- paste0("s(", x.f, ",bs='cr', k=min(10,", unique.x, "))")

  # (1.4) xc included in first specification (<=)
  xlow1  <- ifelse(xu <= xc, xu - xc, 0)
  xhigh1 <- ifelse(xu >  xc, xu - xc, 0)
  high1  <- ifelse(xu >  xc, 1, 0)

  # (1.5) xc included in second specification (<)
  xlow2  <- ifelse(xu <  xc, xu - xc, 0)
  xhigh2 <- ifelse(xu >= xc, xu - xc, 0)
  high2  <- ifelse(xu >= xc, 1, 0)

  # (2) Build and run interrupted regressions
  if (var.count > 2) {
    glm1.f <- update(nox.f, ~ xlow1 + xhigh1 + high1 + .)
    glm2.f <- update(nox.f, ~ xlow2 + xhigh2 + high2 + .)
  }
  if (var.count == 2) {
    glm1.f <- as.formula("yu ~ xlow1 + xhigh1 + high1")
    glm2.f <- as.formula("yu ~ xlow2 + xhigh2 + high2")
  }

  glm1 <- glm(as.formula(format(glm1.f)), family = family)
  glm2 <- glm(as.formula(format(glm2.f)), family = family)

  # (2.3) Robust SEs (HC3, fall back to HC1 if NA)
  rob1 <- coeftest(glm1, vcov = vcovHC(glm1, "HC3"))
  rob2 <- coeftest(glm2, vcov = vcovHC(glm2, "HC3"))

  msg <- ""
  if (is.na(rob1[2, 4])) {
    rob1 <- coeftest(glm1, vcov = vcovHC(glm1, "HC1"))
    msg  <- paste0(msg, "\nLine 1: HC3 failed, used HC1.")
  }
  if (is.na(rob2[2, 4])) {
    rob2 <- coeftest(glm2, vcov = vcovHC(glm2, "HC1"))
    msg  <- paste0(msg, "\nLine 2: HC3 failed, used HC1.")
  }

  b1 <- as.numeric(rob1[2, 1]); z1 <- as.numeric(rob1[2, 3]); p1 <- as.numeric(rob1[2, 4])
  b2 <- as.numeric(rob2[3, 1]); z2 <- as.numeric(rob2[3, 3]); p2 <- as.numeric(rob2[3, 4])

  u.sig <- ifelse(b1 * b2 < 0 & p1 < .05 & p2 < .05, 1, 0)

  # (4) Plot
  if (graph == 1) {
    pch.dot <- 1; col.l1 <- "dodgerblue3"; col.l2 <- "firebrick"
    col.fit <- "gray50"; col.div <- "green3"; lty.fit <- 2

    unique.x <- length(unique(xu))
    sx.f     <- paste0("s(", x.f, ",bs='cr', k=min(10,", unique.x, "))")

    if (var.count == 2) {
      gams  <- gam(as.formula(paste0("yu~", sx.f)))
      yobs  <- yu
      yhat.smooth <- predict.gam(gams)
      offset3     <- mean(yobs - yhat.smooth)
      yhat.smooth <- yhat.smooth + offset3
    }

    y1 <- max(yobs, yhat.smooth); y0 <- min(yobs, yhat.smooth); yr <- y1 - y0; y0 <- y0 - .3 * yr
    x1 <- max(xu); x0 <- min(xu); xr <- x1 - x0

    par(mar = c(5.4, 4.1, .5, 2.1))
    plot(xu[xu < xc], yobs[xu < xc], cex = .75, col = col.l1, pch = pch.dot, las = 1,
         ylim = c(y0, y1), xlim = c(x0, x1), xlab = "", ylab = "")
    points(xu[xu > xc], yobs[xu > xc], cex = .75, col = col.l2)
    mtext(side = 1, line = 2.75, x.f, font = 2)
    mtext(side = 2, line = 2.75, y.f, font = 2)
    lines(xu[order(xu)], yhat.smooth[order(xu)], col = col.fit, lty = 2, lwd = 2)

    xm1 <- (xc + x0) / 2
    x0.a1 <- xm1 - .1 * xr; x1.a1 <- xm1 + .1 * xr
    y0.a1 <- y0 + .1 * yr;  y1.a1 <- y0.a1 + b1 * (x1.a1 - x0.a1)
    if (x0.a1 < x0 + .1 * xr) x0.a1 <- x0
    gap1 <- min(y0.a1, y1.a1) - (y0 + .1 * yr)
    if (gap1 < 0) { y0.a1 <- y0.a1 - gap1; y1.a1 <- y1.a1 - gap1 }
    arrows(x0 = x0.a1, x1 = x1.a1, y0 = y0.a1, y1 = y1.a1, col = col.l1, lwd = 2)
    xm1 <- max(xm1, x0 + .20 * xr)
    text(xm1, y0 + .025 * yr,
         paste0("Average slope 1:\nb = ", round(b1, 2), ", z = ", round(z1, 2), ", ", rp(p1)),
         col = col.l1)

    xm2 <- xc + (x1 - xc) / 2
    x0.a2 <- xm2 - .1 * xr; x1.a2 <- min(xm2 + .1 * xr, x1)
    y0.a2 <- y1.a1; y1.a2 <- y0.a2 + b2 * (x1.a2 - x0.a2)
    gap2 <- min(y0.a2, y1.a2) - (y0 + .1 * yr)
    if (gap2 < 0) { y0.a2 <- y0.a2 - gap2; y1.a2 <- y1.a2 - gap2 }
    if (x0.a2 < xc) x0.a2 <- xc
    xm2 <- min(xm2, x1 - .2 * xr)
    arrows(x0 = x0.a2, x1 = x1.a2, y0 = y0.a2, y1 = y1.a2, col = col.l2, lwd = 2)
    text(xm2, y0 + .025 * yr,
         paste0("Average slope 2:\nb = ", round(b2, 2), ", z = ", round(z2, 2), ", ", rp(p2)),
         col = col.l2)

    lines(c(xc, xc), c(y0 + .35 * yr, y1), col = col.div, lty = lty.fit)
    text(xc, y0 + .3 * yr, round(xc, 2), col = col.div)
  }

  list(b1 = b1, p1 = p1, b2 = b2, p2 = p2, u.sig = u.sig, xc = xc,
       z1 = z1, z2 = z2, glm1 = glm1, glm2 = glm2, rob1 = rob1, rob2 = rob2, msg = msg)
}

# Function 4 — two-lines test (determines breakpoint via Robin Hood algorithm)
twolines <- function(f, graph = 1, link = "gaussian", data = NULL, pngfile = "") {
  attach(data)
  on.exit(detach(data))

  y.f       <- all.vars(f)[1]
  x.f       <- all.vars(f)[2]
  var.count <- length(all.vars(f))
  if (var.count > 2) nox.f <- drop.terms(terms(f), dropx = 1, keep.response = TRUE)

  # Drop missing values
  vars      <- all.vars(f)
  cols      <- sapply(vars, function(v) which(names(data) == v))
  full.rows <- complete.cases(data[, cols])
  data      <- data[full.rows, ]
  detach(data); attach(data); on.exit(detach(data))

  xu <- eval2(x.f)
  yu <- eval2(y.f)

  unique.x <- length(unique(xu))
  sx.f     <- paste0("s(", x.f, ",bs='cr', k=min(10,", unique.x, "))")

  # (2) Fit GAM smoother
  if (var.count > 2) gam.f <- paste0(format(nox.f), "+", sx.f)
  if (var.count == 2) gam.f <- paste0("yu~", sx.f)
  gams <- gam(as.formula(gam.f), family = link)

  # (3) yobs
  if (var.count == 2) yobs <- yu

  # (4) Fitted values and SE
  g.fit <- predict.gam(gams, se.fit = TRUE)
  y.hat <- g.fit$fit
  y.se  <- g.fit$se.fit

  # (5) Find the flat region near the peak/trough
  xu2 <- xu^2
  if (var.count == 2) lmq <- lm(yu ~ xu + xu2)
  bqs <- lmq$coefficients
  s0  <- bqs[2] + 2 * bqs[3] * min(xu)
  shape <- ifelse(s0 > 0, "inv-ushape", "ushape")

  x10    <- quantile(xu, .1); x90 <- quantile(xu, .9)
  middle <- (xu > x10 & xu < x90)
  x.middle <- xu[middle]
  y.hat    <- y.hat[middle]
  y.se     <- y.se[middle]
  y.ub     <- y.hat + y.se
  y.lb     <- y.hat - y.se

  if (shape == "inv-ushape") { y.most <- max(y.hat); flat <- (y.ub > y.most) }
  if (shape == "ushape")     { y.most <- min(y.hat); flat <- (y.lb < y.most) }
  x.most <- x.middle[match(y.most, y.hat)]
  xflat  <- x.middle[flat]

  # (6) Robin Hood breakpoint
  rmid <- reg2(f, xc = median(xflat), graph = 0)
  z1   <- abs(rmid$z1); z2 <- abs(rmid$z2)
  xc   <- quantile(xflat, z2 / (z1 + z2))

  if (pngfile != "") png(pngfile, width = 2000, height = 1500, res = 300)
  res <- reg2(as.formula(format(f)), xc = xc, graph = graph)
  if (pngfile != "") dev.off()

  res$yobs    <- yobs
  res$y.hat   <- y.hat
  res$x.most  <- x.most
  res$f       <- format(f)
  res$midflat <- median(xflat)
  res$midz1   <- abs(rmid$z1)
  res$midz2   <- abs(rmid$z2)
  res
}
