lai_col    = '#009900'
k_cols     = c('#002222', '#005555', '#00AAAA', '#00EEEE')
albedo_col = '#AA0000'

par(mfrow = c(2,1), mar = c(1, 3, 0, 3), oma = c(2, 0, 0.5, 0))

x = seq(0, 12, length.out = 361)

lai = (runif(361, 0, 1) * 0.1 + cos(seq(pi, 3*pi, length.out = 361)))*0.5 + 0.3
lai = 1/(1+exp(-10*(lai - 0.5)))
lai = lai  + 0.15 + runif(361, 0, 0.1)


plot(range(x), c(0, 1), axes = FALSE, type = 'n')	
points(x, lai * 0.8, col = lai_col)
axis(1, 0.5:11.5, c('J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D'))
axis(2, seq(0, 1, 0.2), 0:5)
mtext('LAI', side = 2, line = 2)
axis(4, seq(0, 1, 0.25), seq(0, 100, 25))
mtext('exposed ground (%)', side = 4, line = 2)

	
calSoil <- function(k, col = NULL) {
	soil = exp(- k * 	lai)
	if (!is.null(col)) {	
		lines(x, soil, col = col)
		text(x=6, y=min(soil) - 0.05, k)
	}
	return(soil)
}

soils = mapply(calSoil, c(0.1, 0.5, 1.0, 2.0), k_cols, SIMPLIFY = FALSE)

soil_albedo = 0.3
veg_albedo = 0.2

soilsX = calSoil(1.3)
soilsX = soilsX + runif(361, -0.3, 0.3)


albedo = soil_albedo * soilsX + veg_albedo * (1-soilsX)
albedoP = albedo - min(albedo)
albedoP = albedoP / max(albedoP)
index = seq(0, 360, 8)
lines(x[index], albedoP[index], col = albedo_col, lwd = 2)

plot(c(0, 1), c(0.0,0.35), axes = FALSE, xaxs = 'i', yaxs = 'i', type = 'n')
axis(1, seq(0, 1, 0.2), seq(0, 100, 20))
axis(2)
mtext('exposed ground (%)', side = 1, line = 2)
mtext('Albedo', side = 2, line = 2)

boundedLinear <- function(x, y0, y1) 
	(y1 - y0) * x + y0

plotSoils <- function(soil,  col) {
	x = soil[index]
	y = albedo[index]
	points(x,y, col = col, pch = 19)
	fit = nls(y ~ boundedLinear(x, y0, y1), data = data.frame(x = x, y = y), 
		      lower = c(y0 = 0, y1 = 0), upper = c(y0 = 1, y1 = 1), start = c(y0 = 0.1, y1 = 0.9),
			  algorithm = "port")
			  
	print(fit)
	xline = seq(0, 100)
	yline = predict(fit, newdata = data.frame(x = xline))
	lines(xline, yline, col = col)
}

mapply(plotSoils, soils, col = k_cols)
legend('bottomright', c('    LAI', '0.1', '0.5    light decay', '1.0    coefficient', '2.0', '    Albedo'),
		pch = c(1, 19, 19, 19, 19, 0), lwd = c(NaN, 1, 1, 1, 1, 2), col = c(lai_col, k_cols, albedo_col))