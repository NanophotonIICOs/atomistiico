using LaTeXStrings
using PGFPlotsX
using JSON
using PyCall

function bandsplots(calcjson::String,params::Dict)
    bands = read(calcjson,String)
    data = JSON.parse(bands)
    np = pyimport("numpy")
    bands = np.array(data["energies"])
    xtickcoords =  data["label_xcoords"]

    ini_band = params["ini_band"]
    end_band = params["end_band"]

    if ini_band == 1
        println("The number of initial bands can't be equal to 1!")
        ini_band=2
    end

    if end_band == ini_band
        println("The number of bands are equal!....")
        println("Therefore we plot the number of ini_band + 1, check this in your parameters!")
        end_band = ini_band+1
    elseif end_band< ini_band
        println("The number of final bands to plot is less than initial bands!...")
        println("The end bands parameter is now ini_band +1!")
        end_band = ini_band+1
    end

    
    emin = params["emin"]
    emax = params["emax"]
    xmin = xtickcoords[1]
    xmax = xtickcoords[end]

    p = @pgf TikzPicture(
    Axis(
    { 
        height = "13cm",
        width = "13cm",
        "scale only axis",
        "axis background/.style={fill=none}",
        "line width = 2pt",
        "tick style = {line width=2pt,black}",
        "ticklabel style={scale=1}",
        "major tick length = 2mm",
        "minor tick length = 0.9mm",
        "ylabel style={scale=2}",
        "every tick label/.append style={scale=1.5}",
        "every axis plot/.style={smooth,mark options={scale=1.},line width=1.5pt}",
        xmin=xmin,xmax=xmax,
        ymin=emin,ymax=emax,
        xtick = xtickcoords,
        xticklabels =data["x_labels"],
        xmajorgrids,
        "major x grid style={gray,thick}",
        ylabel = L"$\epsilon - \epsilon_{F}$ (eV)",
        #Legend style
        "every axis legend/.style={
            cells={anchor=center},
            inner xsep=1pt,
            inner ysep=1pt,
            nodes={scale=1.5,inner sep=2pt, transform shape},
            draw=none,
            fill=white,
            at={(1,0.05)},
            anchor=south east,
        }",
    },
    #[raw"\addlegendimage",{\uparrow,\downarrow}],
    #spin Down
    [Plot({blue,no_marks,forget_plot},Table("x"=>bands[1,:,1],"y"=>bands[1,:,k])) for k=ini_band:end_band-1],
    Plot({blue,no_marks},Table("x"=>bands[1,:,1],"y"=>bands[1,:,end_band])),
    LegendEntry(L"\color{blue}{Spin $\uparrow$}"),
    #spin Up
    [Plot({red,no_marks,forget_plot},Table("x"=>bands[2,:,1],"y"=>bands[2,:,k])) for k=ini_band:end_band-1],
    Plot({red,no_marks},Table("x"=>bands[2,:,1],"y"=>bands[2,:,end_band])),
    LegendEntry(L"\color{red}{Spin $\downarrow$}")
    ),
    )
end