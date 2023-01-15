using LaTeXStrings
using PGFPlotsX
using JSON
using PyCall
using DataFrames
include("export_plots.jl")


params_default= Dict(
    "emin" => -2,
    "emax" =>  3,
    "xmin" =>  0.0,
    "xmax" =>  3.0,
    "initial_band" => 10,
    "final_band"   => 80,
    "height" => "13cm",
    "width" =>  "15cm",
    "scale_only_axis" => false,
    "width_plot_with_dos"=> "4cm",
    "ax_lw" => "1.5pt",                 # axis line width in cm
    "ax_size_minor_tick" => "1.0mm",   # minor tick size in mm
    "ax_size_major_tick" => "2.0mm",   # majot tick size in mm
    "ax_tick_scale"      => 1.2,
    "ax_labels_scale"    => 1.5,
    "ax_xmajorgrids"     => true,
    "ax_legend_position" => (1,0.01),
    "ax_legend_anchor"   => "south east",
    "ax_ylabel"          =>  L"$E-E_{F}$ (eV)",
    "ax_plot_line_width" => "2pt",
    "ax_plot_mark_scale" => 1,
    "ax_plot_title_scale" => 2,
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
    xtickcoords = data["label_xcoords"]
    plot_title  = data["name"]
    parameters = plot_params(params)
    update_parameters(parameters,"xmin",float(xtickcoords[1]))
    update_parameters(parameters,"xmax",float(xtickcoords[end]))

    if parameters["initial_band"] > size(bands,3)
        update_parameters(parameters,"initial_band",2)
        println("The number of initial band is greath than size of bands array") 
    elseif parameters["final_band"] > size(bands,3)
        total_calc_bands = size(bands,3)
        update_parameters(parameters,"final_band",total_calc_bands)
        println("The number of final band to plots are excess of number of calculate bands!\n
                 Therefore the final band to plot is the number of total calculate bands:$(total_calc_bands)")
    end


    #fermi level coordinates
    xf =[parameters["xmin"],parameters["xmax"]]
    yf =[0,0] 
    plot = @pgf TikzPicture(
    Axis(
    { 
        height = parameters["height"],
        width  = parameters["width"],
        #-------------------------------------------------------------------------
        "scale only axis" = parameters["scale_only_axis"],
        "axis background/.style={fill=none}",
        line_width        = "{$(parameters["ax_lw"])}",
        tick_style        = "{line width=$(parameters["ax_lw"]),black}",
        ticklabel_style   = "{scale=$(parameters["ax_tick_scale"])}",
        major_tick_length = "{$(parameters["ax_size_major_tick"])}",
        minor_tick_length = "{$(parameters["ax_size_minor_tick"])}",
        ylabel_style      = "{scale=$(parameters["ax_labels_scale"])}",
        # "every tick label/.append style={scale=1.5}",
        "every axis plot/.style"="{
                smooth,
                mark options={scale=$(parameters["ax_plot_mark_scale"])},
                line width=$(parameters["ax_plot_line_width"])}",
        # -------------------------------------------------------------------------
        xmin=parameters["xmin"],xmax=parameters["xmax"],
        ymin=parameters["emin"],ymax=parameters["emax"],
        xtick = xtickcoords,
        xticklabels =data["x_labels"],
        xmajorgrids,
        "major x grid style={gray,thick}",
        ylabel = L"E - E_{F}$ (eV)",
        #Legend style
        "every axis legend/.style" = "{
                                        cells={anchor=center},
                                        inner xsep=1pt,
                                        inner ysep=1pt,
                                        nodes={scale=$(parameters["ax_labels_scale"]),inner sep=2pt, transform shape},
                                        draw=none,
                                        fill=white,
                                        at={$(parameters["ax_legend_position"])},
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
    xtickcoords = data["label_xcoords"]
    plot_title  = data["name"]
    parameters = plot_params(params)
    update_parameters(parameters,"xmin",float(xtickcoords[1]))
    update_parameters(parameters,"xmax",float(xtickcoords[end]))
    dos_up_max, dos_down_max = data["dos_max"]
    #fermi level coordinates
    xf = [parameters["xmin"],parameters["xmax"]]
    yf = [0,0] 

    if parameters["initial_band"] > size(bands,3)
        update_parameters(parameters,"initial_band",2)
        println("The number of initial band is greath than size of bands array") 
    elseif parameters["final_band"] > size(bands,3)
        total_calc_bands = size(bands,3)
        update_parameters(parameters,"final_band",total_calc_bands)
        println("The number of final band to plots are excess of number of calculate bands!")
        println("Therefore the final band to plot is the number of total calculate bands:$(total_calc_bands)")
    end

    push!(PGFPlotsX.CUSTOM_PREAMBLE, raw"\usepgfplotslibrary{fillbetween}")
    plot = @pgf TikzPicture(
        Axis(
        { 
            "name=plot1",
            height = parameters["height"],
            width  = parameters["width"],
            title  = "$(plot_title)",
            title_style ="{scale=$(parameters["ax_labels_scale"]),at={(axis description cs:0.5,1.05)}}",
            #-------------------------------------------------------------------------
            "scale only axis" = parameters["scale_only_axis"],
            "axis background/.style={fill=none}",
            line_width        = "{$(parameters["ax_lw"])}",
            tick_style        = "{line width=$(parameters["ax_lw"]),black}",
            ticklabel_style   = "{scale=$(parameters["ax_tick_scale"])}",
            major_tick_length = "{$(parameters["ax_size_major_tick"])}",
            minor_tick_length = "{$(parameters["ax_size_minor_tick"])}",
            ylabel_style      = "{scale=$(parameters["ax_labels_scale"])}",
            "ytick pos = left",
            # "every tick label/.append style={scale=1.5}",
            "every axis plot/.style"="{
                    smooth,
                    mark options={scale=$(parameters["ax_plot_mark_scale"])},
                    line width=$(parameters["ax_plot_line_width"])}",
            # -------------------------------------------------------------------------
            xmin=parameters["xmin"],xmax=parameters["xmax"],
            ymin=parameters["emin"],ymax=parameters["emax"],
            xtick = xtickcoords,
            xticklabels =data["x_labels"],
            xmajorgrids,
            "major x grid style={gray,thick}",
            ylabel = L"$\epsilon - \epsilon_{F}$ (eV)",
            #Legend style
            "every axis legend/.style" = "{
                                            cells={anchor=center},
                                            inner xsep=1pt,
                                            inner ysep=1pt,
                                            nodes={scale=$(parameters["ax_labels_scale"]),inner sep=2pt, transform shape},
                                            draw=none,
                                            fill=white,
                                            at={$(parameters["ax_legend_position"])},
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
        "anchor = south west",
        "at={(plot1.south east)}",
        height = parameters["height"],
        width  = parameters["width_plot_with_dos"],
        "axis background/.style={fill=none}",
        "axis line style" = "{line width=$(parameters["ax_lw"])}",
        "clip mode = individual",
        tick_style        = "{line width=$(parameters["ax_lw"]),black}",
        ticklabel_style   = "{scale=$(parameters["ax_tick_scale"])}",
        major_tick_length = "{$(parameters["ax_size_major_tick"])}",
        minor_tick_length = "{$(parameters["ax_size_minor_tick"])}",
        ylabel_style      = "{scale=$(parameters["ax_labels_scale"]),rotate=180}",
        xlabel_style      = "{scale=$(parameters["ax_labels_scale"])}",
        # "every tick label/.append style={scale=1.5}",
        "every axis plot/.style"="{
                smooth,
                mark options={scale=$(parameters["ax_plot_mark_scale"])},
                line width=$(parameters["ax_plot_line_width"])}",
        "xtick pos = right",
        "ytick pos = right",
        ymin=parameters["emin"],ymax=parameters["emax"],
        xmin=-dos_down_max,xmax=dos_up_max,
        # "axis line style = {line width=2pt}",
        # "clip mode = individual",
         ylabel = L"$E - E_{F}$ (eV)",
        "xlabel = DOS",
    },
        [Plot({red,no_marks,"name path=up"},Table("x"=>dos[1,:,2],"y"=>dos[1,:,1]))],
        [Plot({blue,no_marks,"name path=down"},Table("x"=>dos[2,:,2],"y"=>dos[2,:,1]))],
        raw"\path[name path=axis] (axis cs:0,0) -- (axis cs:0,0);",
        Plot({ thick, color = "red", fill = "red", opacity = 0.25 },raw"fill between [of=up and axis]"),
        Plot({ thick, color = "blue", fill = "blue", opacity = 0.25 },raw"fill between [of=down and axis]"),
    )
)

return plot
end





function bandsplots_with_dos_bubble(dir_calc::String,params::Dict)
    data        = read_calcfile(dir_calc)
    np          = pyimport("numpy")
    bands       = np.array(data["energies"])
    dos         = np.array(data["dos"])
    xtickcoords = data["label_xcoords"]
    plot_title  = data["name"]
    parameters = plot_params(params)
    update_parameters(parameters,"xmin",float(xtickcoords[1]))
    update_parameters(parameters,"xmax",float(xtickcoords[end]))
    dos_up_max, dos_down_max = data["dos_max"]
    #fermi level coordinates
    xf = [parameters["xmin"],parameters["xmax"]]
    yf = [0,0] 

    
    if parameters["initial_band"] > size(bands,3)
        update_parameters(parameters,"initial_band",2)
        println("The number of initial band is greath than size of bands array") 
    elseif parameters["final_band"] > size(bands,3)
        total_calc_bands = size(bands,3)
        update_parameters(parameters,"final_band",total_calc_bands)
        println("The number of final band to plots are excess of number of calculate bands!")
        println("Therefore the final band to plot is the number of total calculate bands:$(total_calc_bands)")
    end

    push!(PGFPlotsX.CUSTOM_PREAMBLE, raw"\usepgfplotslibrary{fillbetween}")
    plot = @pgf TikzPicture(
    Axis(
        { 
            "name=plot1",
            height = parameters["height"],
            width  = parameters["width"],
            title  = "$(plot_title)",
            title_style ="{scale=$(parameters["ax_labels_scale"]),at={(axis description cs:0.5,1.05)}}",
            #-------------------------------------------------------------------------
            "scale only axis" = parameters["scale_only_axis"],
            "axis background/.style={fill=none}",
            line_width        = "{$(parameters["ax_lw"])}",
            tick_style        = "{line width=$(parameters["ax_lw"]),black}",
            ticklabel_style   = "{scale=$(parameters["ax_tick_scale"])}",
            major_tick_length = "{$(parameters["ax_size_major_tick"])}",
            minor_tick_length = "{$(parameters["ax_size_minor_tick"])}",
            ylabel_style      = "{scale=$(parameters["ax_labels_scale"])}",
            "ytick pos = left",
            # "every tick label/.append style={scale=1.5}",
            "every axis plot/.style"="{
                    smooth,
                    mark options={scale=$(parameters["ax_plot_mark_scale"])},
                    line width=$(parameters["ax_plot_line_width"])}",
            # -------------------------------------------------------------------------
            xmin=parameters["xmin"],xmax=parameters["xmax"],
            ymin=parameters["emin"],ymax=parameters["emax"],
            xtick = xtickcoords,
            xticklabels =data["x_labels"],
            xmajorgrids,
            "major x grid style={gray,thick}",
            ylabel = L"$E - E_{F}$ (eV)",
            #Legend style
            "every axis legend/.style" = "{
                                            cells={anchor=center},
                                            inner xsep=1pt,
                                            inner ysep=1pt,
                                            nodes={scale=$(parameters["ax_labels_scale"]),inner sep=2pt, transform shape},
                                            draw=none,
                                            fill=white,
                                            at={$(parameters["ax_legend_position"])},
                                            anchor=south east,
                                           }",
        },
            #spin Up
            #[Plot({ "scatter=true",
            #         "mark=*",
            #         "color=red",
            #         raw"point meta=explicit symbolic",
            #         raw"scatter/@pre marker code/.append style={/tikz/mark size=\pgfplotspointmeta/1}",
            #         raw"scatter/@post marker code/.code={\endscope}",
            #         forget_plot
            #       },Table({"meta=y"},"x"=>bands[1,:,1],"y"=>bands[1,:,k])) for k=parameters["initial_band"]:parameters["final_band"]-1],
            [Plot({ 
                        "scatter",
                        "mark=*",
                        "only marks",
                        "scatter/use mapped color={draw=red,fill=red,fill opacity=1}",
                        "scatter src=y",
                        "mark options={line width=1pt}",
                        raw"visualization depends on={2*sin(deg(y)) \as \perpointmarksize}",
                        raw"scatter/@pre marker code/.append style={/tikz/mark size=\perpointmarksize},",
                        forget_plot
                    },Table("x"=>bands[1,:,1],"y"=>bands[1,:,k])) for k=parameters["initial_band"]:parameters["final_band"]-1],
            Plot({ "scatter",
                    "mark=*",
                    "only marks",
                    "scatter/use mapped color={draw=red,fill=red}",
                    "mark options={draw=red,fill=red,line width=1pt}",
                    raw"visualization depends on={2*sin(deg(y)) \as \perpointmarksize}",
                    raw"scatter/@pre marker code/.append style={/tikz/mark size=\perpointmarksize},",
                 },Table("x"=>bands[1,:,1],"y"=>bands[1,:,parameters["final_band"]])),
            LegendEntry(L"\color{red}{Spin $\uparrow$}"),
            #fermi level
            Plot({forget_plot, no_marks,dashed},Coordinates(xf,yf)),
            #spin Down
            [PlotInc({ 
                        "scatter",
                        "mark=*",
                        "only marks",
                        "scatter/use mapped color={draw=blue,fill=blue,fill opacity=1}",
                        "scatter src=y",
                        "mark options={line width=1pt}",
                        raw"visualization depends on={2*sin(deg(y)) \as \perpointmarksize}",
                        raw"scatter/@pre marker code/.append style={/tikz/mark size=\perpointmarksize},",
                        forget_plot
                    },Table({"meta=y"},"x"=>bands[2,:,1],"y"=>bands[2,:,k])) for k=parameters["initial_band"]:parameters["final_band"]-1],
            Plot({ "scatter",
                    "mark=*",
                    "only marks",
                    "scatter/use mapped color={draw=blue,fill=blue}",
                    "mark options={draw=blue,fill=blue,line width=1pt}",
                    raw"visualization depends on={2*sin(deg(y)) \as \perpointmarksize}",
                    raw"scatter/@pre marker code/.append style={/tikz/mark size=\perpointmarksize},",
                 },Table("x"=>bands[1,:,1],"y"=>bands[1,:,parameters["final_band"]])),
            LegendEntry(L"\color{blue}{Spin $\downarrow$}"),
        ),
Axis(
    {
        height = parameters["height"],
        width  = parameters["width_plot_with_dos"],
        "anchor = south west",
        "at={(plot1.south east)}",
        "axis background/.style={fill=none}",
        "axis line style" = "{line width=$(parameters["ax_lw"])}",
        "clip mode = individual",
        tick_style        = "{line width=$(parameters["ax_lw"]),black}",
        ticklabel_style   = "{scale=$(parameters["ax_tick_scale"])}",
        major_tick_length = "{$(parameters["ax_size_major_tick"])}",
        minor_tick_length = "{$(parameters["ax_size_minor_tick"])}",
        ylabel_style      = "{scale=$(parameters["ax_labels_scale"]),rotate=180}",
        xlabel_style      = "{scale=$(parameters["ax_labels_scale"])}",
        # "every tick label/.append style={scale=1.5}",
        "every axis plot/.style"="{
                smooth,
                mark options={scale=$(parameters["ax_plot_mark_scale"])},
                line width=$(parameters["ax_plot_line_width"])}",
        "xtick pos = right",
        "ytick pos = right",
        ymin=parameters["emin"],ymax=parameters["emax"],
        xmin=-dos_down_max,xmax=dos_up_max,
        # "axis line style = {line width=2pt}",
        # "clip mode = individual",
         ylabel = L"$E - E_{F}$ (eV)",
        "xlabel = DOS",
    },
        [Plot({red,no_marks,"name path=up"},Table("x"=>dos[1,:,2],"y"=>dos[1,:,1]))],
        [Plot({blue,no_marks,"name path=down"},Table("x"=>dos[2,:,2],"y"=>dos[2,:,1]))],
        raw"\path[name path=axis] (axis cs:0,0) -- (axis cs:0,0);",
        Plot({ thick, color = "red", fill = "red", opacity = 0.25 },raw"fill between [of=up and axis]"),
        Plot({ thick, color = "blue", fill = "blue", opacity = 0.25 },raw"fill between [of=down and axis]"),
    )
)
return plot
end

