using LaTeXStrings
using PGFPlotsX
using JSON
using PyCall

params_default= Dict(
    "emin" => -3,
    "emax" =>  3,
    "xmin" =>  0.0,
    "xmax" =>  3.0,
    "initial_band" => 2,
    "final_band"   => 2+1,
    "height" => 10,
    "width" => 10,
    "width_plot_with_dos"=>3.0,
)

function update_parameters(params::Dict, key, value)
    if haskey(params, key)
        params[key] = value
    # else
    #     error_mesage = "$key does not exist in parameters!"
    #     raise KeyError(error_mesage)
    end
end

function plot_params(params::Dict)
    for (key,value) in params_default
        if !haskey(params,key)
            params[key] = value
        end
    end


    if params["initial_band"] == 1
        println("The number of initial band can't be equal to 1, this parameter will be changed to 2! ")
        params["initial_band"] = 2

    elseif params["initial_band"] == params["final_band"]
        println("The number of bands are equal!....")
        println("Therefore we plot the number of ini_band + 1, check this in your parameters!")
        params["final_band"] = params["inital_band"] + 1

    elseif params["final_band"] < params["initial_band"]
        println("The number of final band to plot is less than initial bands!...")
        println("The end band parameter is now ini_band +1!")
        params["final_band"] = params["inital_band"] + 1
    end

    return params
end

function read_calcfile(dir_calc::String)
    file = read(dir_calc,String)
    data = JSON.parse(file)
    return data
end

function bandsplots(dir_calc::String,params::Dict)
    data        = read_calcfile(dir_calc)
    np          = pyimport("numpy")
    bands       = np.array(data["energies"])
    xtickcoords =  data["label_xcoords"]
    parameters = plot_params(params)
    update_parameters(parameters,"xmin",float(xtickcoords[1]))
    update_parameters(parameters,"xmax",float(xtickcoords[end]))

    #fermi level coordinates
    xf =[parameters["xmin"],parameters["xmax"]]
    yf =[0,0] 

    p = @pgf TikzPicture(
    Axis(
    { 
        height = string(parameters["height"])*"cm",
        width = string(parameters["width"])*"cm",
        #-------------------------------------------------------------------------
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
        # -------------------------------------------------------------------------
        xmin=parameters["xmin"],xmax=parameters["xmax"],
        ymin=parameters["emin"],ymax=parameters["emax"],
        xtick = xtickcoords,
        xticklabels =data["x_labels"],
        xmajorgrids,
        "major x grid style={gray,thick}",
        ylabel = L"$\epsilon - \epsilon_{F}$ (eV)",
        #Legend style
        "every axis legend/.style=
        {
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
    #spin Up
    [Plot({red,no_marks,forget_plot},Table("x"=>bands[1,:,1],"y"=>bands[1,:,k])) for k=parameters["initial_band"]:parameters["final_band"]-1],
    Plot({red,no_marks},Table("x"=>bands[1,:,1],"y"=>bands[1,:,parameters["final_band"]])),
    LegendEntry(L"\color{red}{Spin $\uparrow$}"),
    # fermi_level
    Plot({forget_plot, no_marks,dashed},Coordinates(xf,yf)),
    #spin down
    [Plot({blue,no_marks,forget_plot},Table("x"=>bands[2,:,1],"y"=>bands[2,:,k])) for k=parameters["initial_band"]:parameters["final_band"]-1],
    Plot({blue,no_marks},Table("x"=>bands[2,:,1],"y"=>bands[2,:,parameters["final_band"]])),
    LegendEntry(L"\color{blue}{Spin $\downarrow$}")
    ),
    )
end


function bandsplots_with_dos(dir_calc::String,params::Dict)
    data        = read_calcfile(dir_calc)
    np          = pyimport("numpy")
    bands       = np.array(data["energies"])
    dos         = np.array(data["dos"])
    xtickcoords =  data["label_xcoords"]
    parameters = plot_params(params)
    update_parameters(parameters,"xmin",float(xtickcoords[1]))
    update_parameters(parameters,"xmax",float(xtickcoords[end]))
    dos_up_max, dos_down_max = data["dos_max"]
    #fermi level coordinates
    xf = [parameters["xmin"],parameters["xmax"]]
    yf = [0,0] 

    push!(PGFPlotsX.CUSTOM_PREAMBLE, raw"\usepgfplotslibrary{fillbetween}")
    p = @pgf TikzPicture(
        Axis(
        { 
            "name=plot1",
            height = string(parameters["height"])*"cm",
            width = string(parameters["width"])*"cm",
            #-------------------------------------------------------------------------
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
            "ytick pos = left",
            # -------------------------------------------------------------------------
            xmin=parameters["xmin"],xmax=parameters["xmax"],
            ymin=parameters["emin"],ymax=parameters["emax"],
            xtick = xtickcoords,
            xticklabels =data["x_labels"],
            xmajorgrids,
            "major x grid style={gray,thick}",
            ylabel = L"$\epsilon - \epsilon_{F}$ (eV)",
            #Legend style
            "every axis legend/.style=
            {
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
         #spin Up
        [Plot({red,no_marks,forget_plot},Table("x"=>bands[1,:,1],"y"=>bands[1,:,k])) for k=parameters["initial_band"]:parameters["final_band"]-1],
        Plot({red,no_marks},Table("x"=>bands[1,:,1],"y"=>bands[1,:,parameters["final_band"]])),
        LegendEntry(L"\color{red}{Spin $\uparrow$}"),
        #fermi level
        Plot({forget_plot, no_marks,dashed},Coordinates(xf,yf)),
        #spin Down
        [Plot({blue,no_marks,forget_plot},Table("x"=>bands[2,:,1],"y"=>bands[2,:,k])) for k=parameters["initial_band"]:parameters["final_band"]-1],
        Plot({blue,no_marks},Table("x"=>bands[2,:,1],"y"=>bands[2,:,parameters["final_band"]])),
        LegendEntry(L"\color{blue}{Spin $\downarrow$}")
        ),
Axis(
    {
        height = string(parameters["height"])*"cm",
        width  = string(parameters["width_plot_with_dos"])*"cm",
        "anchor = south west",
        "at={(plot1.south east)}",
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
        "xtick pos = right",
        "ytick pos = right",
        ymin=parameters["emin"],ymax=parameters["emax"],
        xmin=-dos_down_max,xmax=dos_up_max,
        "axis line style = {line width=2pt}",
        "clip mode = individual",
    },
        [Plot({red,no_marks,"name path=up"},Table("x"=>dos[1,:,2],"y"=>dos[1,:,1]))],
        [Plot({blue,no_marks,"name path=down"},Table("x"=>dos[2,:,2],"y"=>dos[2,:,1]))],
        raw"\path[name path=axis] (axis cs:0,0) -- (axis cs:0,0);",
        Plot({ thick, color = "red", fill = "red", opacity = 0.25 },raw"fill between [of=up and axis]"),
        Plot({ thick, color = "blue", fill = "blue", opacity = 0.25 },raw"fill between [of=down and axis]"),
    )
)
end
