library(animation)
library(rasterPlot)
library(gitBasedProjects)

p_rock = 0.3
p_paper = 0.1
p_scissors = 0.6

x = seq(0, 1, 0.01)
p0 = rep(1, length(x))

p = list(Rock = p0, Paper = p0, Scissors = p0)

results = c(1, 3, 1, sample(1:3, 96, TRUE, c(p_rock, p_paper, p_scissors)), 3)
totals = rep(0, 3)

plotAt = c(1, 2, 10, 100)


tPlot = rep(FALSE, length(results))
tPlot[plotAt] = TRUE

cols = c("brown", "cyan", "green")

plotN = 0
newGiff <- function() {
	if (plotN > 0) {
		my_command = paste('C:/"Program Files"/ImageMagick-7.0.8-Q16/convert.exe ', plotDir, '/*.png -delay 20 -loop 2 rps/filtering-', plotN, '.gif', sep = '')
		system(my_command)
	}
	plotN <<- plotN +1
	plotDir <<- paste('rps/bayes_image_', plotN, '/', sep = '')
	makeDir(plotDir)
}
newGiff() 

updateResult <- function(res = NaN, n = 0, tPlot = TRUE) {
	if (n < 10) 
		np = paste('00', n , sep = '')
	else if (n < 100)
		np = paste('0', n, sep = '')
	else np = n
	png(paste(plotDir, 'p', np, '.png', sep = ''), unit = 'in', res = 200, height = 5, width = 5)
	par(mfrow = c(3,1), mar = c(1, 3, 0, 1), oma = c(2, 0, 1, 0))
	labs = rep('', 3)
	if (!is.na(res)) {
		ps <<- p
		p[[res]] = p[[res]]* seq(0, 1, length.out = length(x))
		p[-res] = lapply(p[-res], function(i) i * seq(1, 0, length.out = length(x)))
		
		p = lapply(p, function(i) i/max(i))
		p <<- p
		
		labs[res] = paste(names(p)[res], '!', sep = '')
		
		totals[res] = totals[res] + 1
		totals <<- totals
	}
	
	
	plotDist <- function(p,name, lab, total, col) {
		p = p / max(p)
		prange = range(p) + 0.000001 * c(-1, 0.0)
		plot(x, p, axes = FALSE, ylim = prange, lwd = 2, type = 'n')
		mtext(side = 2, line = 1, name)
		polygon(c(x, rev(x)), c(p, rep(-9E9, length(p))), col = make.transparent(col, 0.6), border = NA)
		lines(x, p, col = col, lwd = 2)
		axis(1, at = seq(0, 1, 0.2), labels = rep('', 6))	
		axis(2, at = prange, labels = c('', ''))
		mtext(side = 4, cex = 2, lab)
		mtext(total, side = 3, adj = 0.1, line = -3)
	}
	
	mapply(plotDist, p, names(p), labs, totals, col = cols)
	axis(1, at = seq(0, 1, 0.2))
	
	dev.off()
	if (tPlot) newGiff() 
	print(n)
	return(p)
}

updateResult()
mapply(updateResult, results, (1:length(results)), tPlot)
 my_command <- 'C:/"Program Files"/ImageMagick-7.0.8-Q16/convert.exe rps/*.png -delay 5 -loop 2 filtering.gif'
