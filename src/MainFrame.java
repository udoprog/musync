import java.awt.*;
import javax.swing.*;        
import java.io.StringReader;
import java.awt.event.*;
import java.util.ArrayList;

/**
 * Copyright: John-John Tedro, Oscar Eriksson (2008)
 *
 *   This file is part of musync-swing.
 *
 *   musync-swing is free software: you can redistribute it and/or modify
 *   it under the terms of the GNU General Public License as published by
 *   the Free Software Foundation, either version 3 of the License, or
 *   (at your option) any later version.
 *
 *   musync-swing is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *   GNU General Public License for more details.
 *
 *   You should have received a copy of the GNU General Public License
 *   along with musync-swing.  If not, see <http://www.gnu.org/licenses/>.
 */
class MainFrame extends JFrame implements ActionListener
{
    private Container root;
    private MainOperations ops;
    public MainCenter center; // Need to set options.
    private JButton run, kill;
    private RunXtermWMusync x;

    /**
     * Create the GUI and show it. 
     * For thread safety, this method should be invoked from the
     * event-dispatching thread.
     */
    public MainFrame()
    {
        //Create and set up the window.
        super("Musync - Swing GUI");

        root = getContentPane();
        
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setResizable(true);

        // Main container to put everything in.
        root.setLayout(new BorderLayout());
        
        center = new MainCenter();
        root.add(center, BorderLayout.CENTER);

        createMenuBar();
        createOperationsPanel();
        createButtonPanel();
    }

    /**
     * Create operations panel.
     */
    private void createOperationsPanel()
    {
        ops = new MainOperations();

        return;
    }

    /**
     * Create button panel.
     */
    private void createButtonPanel()
    {
        JPanel panel = new JPanel();
        panel.setBorder(BorderFactory.createMatteBorder(1, 0, 0, 0, new Color(0x999999)));
        panel.setLayout(new FlowLayout(FlowLayout.LEADING, 4, 0));
        
        run = new JButton("run");
        kill = new JButton("kill");

        run.addActionListener(this);
        kill.addActionListener(this);

        panel.add(run);
        panel.add(kill);
        panel.add(ops);
        
        root.add(panel, BorderLayout.PAGE_END);

        return;
    }

    /**
     * Create menu bar.
     */
    private void createMenuBar()
    {
        root.add(new MainMenu(), BorderLayout.PAGE_START);

        return;
    }

    /**
     * Catch all events important to the main frame.
     * This is an internal method and is therefore never used explicitly. The main purpose 
     * for MainFrame to catch an event is to actually 'run' musync.
     *
     * @param e Event object.
     */
    public void actionPerformed(ActionEvent e) {
        Object src = e.getSource();
        if (src == run) {
            if (x != null) {
                if (!x.isAlive()) {
                    x = null;
                } else {
                    Commons.epopup("musync already running, please use 'kill' to stop it");
                    return;
                }
            }

            String files = this.center.files.serialize();
            String opts = this.center.opts.serialize();

            if (opts == null)
                return;
            
            String ops = this.ops.serialize();
            
            if (ops == null)
                return;

            String[] meta = Commons.tmp_meta.serialize();
            String[] commands = new String[5];
            
            java.lang.StringBuilder args = new java.lang.StringBuilder();

            // append options
            args.append(opts + " ");
            
            // append metadata modifiers
            for (String m : meta)
                args.append(m + " ");

            // append operation
            args.append(ops + " ");

            // append files
            args.append(files);

            String musync_command = "musync " + args.toString();
            
            commands[0] = "xterm";
            commands[1] = "-title";
            commands[2] = musync_command;
            commands[3] = "-e";
            commands[4] = musync_command + "; read -p 'press 'enter' to quit'; exit 100";
            x = new RunXtermWMusync(commands);
            x.start();
        }

        // Close the output window.
        if (src == kill) {
            if (x != null) {
                x.kill();
                x = null;
            }
        }
    }
}
