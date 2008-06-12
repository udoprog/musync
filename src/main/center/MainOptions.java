import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.util.HashMap;

/**
 * Creates and handles all the check boxes representing the options to be 
 * sent to musync.
 *
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
public class MainOptions extends JPanel implements ActionListener
{
    private JCheckBox force;
    private JCheckBox silent;
    private JCheckBox recursive;
    private JCheckBox coloring;
    private JCheckBox root;
    private JCheckBox config;
    private JCheckBox fix_log;
    private JCheckBox pretend;
    private JCheckBox lock;
   
    private JPanel optlayout;

    private String targetroot;

    private String root_s;
    private String config_s;
    private String fix_log_s;

    private HashMap<String, String> conf;

    /**
     * The constructor calls the method to create the check boxes
     * and then adds them to the pane.
     */
    public MainOptions()
    {
        super();

        setLayout(new BorderLayout());

        optlayout = new JPanel();
        optlayout.setLayout(new GridLayout(3,0));
        optlayout.setBorder(BorderFactory.createEmptyBorder(4,4,4,4));

        buildCheckboxes();

        optlayout.add(force);
        optlayout.add(silent);
        optlayout.add(pretend);
        optlayout.add(recursive);
        optlayout.add(coloring);
        optlayout.add(lock);
        optlayout.add(root);
        optlayout.add(config);
        optlayout.add(fix_log);

        add(Commons.buildLogo(), BorderLayout.LINE_START);
        add(optlayout, BorderLayout.CENTER);
    }

    /**
     * Builds all usable checkboxes and adds tool tips to them.
     */
    private void buildCheckboxes()
    {
        recursive = new JCheckBox("Recursive (-R)");
        recursive.setToolTipText(
            "Recursion makes musync enter all directories " + 
            "encountered in arguments"
        );
        
        pretend = new JCheckBox("Pretend (-p)");
        pretend.setToolTipText(
            "Pretend - don't actually do anything"
        );
        
        silent = new JCheckBox("Silent (-s)");
        silent.setToolTipText(
            "Silent option makes musync supress the kinds of output listed in 'supress'"
        );
        

        force = new JCheckBox("Force (-f)");
        force.setToolTipText(
            "Force options is used in various cases which " + 
            "musync will tell you about."
        );
        
        lock = new JCheckBox("Lock (-l)");
        lock.setToolTipText(
            "Lock all files on their new position if they have been moved" 
        );
        
        coloring = new JCheckBox("Colored output (-C)");
        coloring.setToolTipText(
            "Use colored output in terminal"
        );
       
        // Below are those with actionlisteners, which requires input from the user.
        root = new JCheckBox("Root (-r)");
        root.addActionListener(this);
        root.setToolTipText(
            "Set which root directory to use, this is the reference to your database"
        );
        
        config = new JCheckBox("Config (-c)");
        config.addActionListener(this);
        config.setToolTipText(
            "Selects which configurations to use (see musync.conf)"
        );
        
        fix_log = new JCheckBox("Fix-Log (-l)");
        fix_log.addActionListener(this);
        fix_log.setToolTipText(
            "Specify where the fix-log (for bad metadata) is going to be written."
        );

        return;
    }

    /**
     * What to do when the user selects an options which requires input.
     *
     * @param e The event.
     */
    public void actionPerformed(ActionEvent e) {
        Object src = e.getSource();

        if (src == fix_log) {
            if (fix_log.isSelected()) {
                if (conf != null && fix_log_s == null)
                    fix_log_s = conf.get("fix-log");
                fix_log_s = JOptionPane.showInputDialog(this, "Type where you wan't the 'fix-log' to end up", fix_log_s);
                if (fix_log_s == null)
                    fix_log.setSelected(false);
            }
            return;
        }
        
        if (src == root) {
            if (root.isSelected()) {
                if (conf != null && root_s == null)
                    root_s = conf.get("root");
                root_s = JOptionPane.showInputDialog(this, "Type what target 'root' you wan't", root_s);
                if (root_s == null)
                    root.setSelected(false);
            }
            return;
        }
        
        if (src == config) {
            if (config.isSelected()) {
                if (conf != null && config_s == null)
                    config_s = conf.get("default-config");
                config_s = JOptionPane.showInputDialog(this, "Type what configurations you wan't to use (seperated by comma)", config_s);
                if (config_s == null)
                    config.setSelected(false);
            }
            return;
        }
        
        return;
    }

    /**
     * Reads all checkboxes and returns a string containing options that musync will accept.
     *
     * @return A space seperated string of selected options to be sent to musync.
     */
    public String serialize()
    {
        StringBuilder ser = new StringBuilder();
        
        if (recursive.isSelected())
            ser.append("-R ");
        if (silent.isSelected())
            ser.append("-s ");
        if (force.isSelected())
            ser.append("-f ");
        if (pretend.isSelected())
            ser.append("-p ");
        if (lock.isSelected())
            ser.append("-l ");
        if (coloring.isSelected())
            ser.append("-C ");
        if (root.isSelected()) {
            if (root_s == null || root_s.equals("")) {
                Commons.epopup("Root directory is not specified, but 'Root' is checked\nTry again.");       
                return null;
            }
            ser.append("-r " + root_s + " ");
        }
        if (config.isSelected()) {
            if (config_s == null || config_s.equals("")) {
                Commons.epopup("Configuration string is not specified, but 'Config' is checked\nTry again.");       
                return null;
            }
            ser.append("-c " + config_s + " ");
        }
        if (fix_log.isSelected()) {
            if (fix_log_s == null || fix_log_s.equals("")) {
                Commons.epopup("Fix log has not been specified but 'Fix-log' is checked\nTry again.");       
                return null;
            }
            ser.append("-l " + fix_log_s + " ");
        }

        if (ser.length() == 1)
            return "";

        return ser.toString();
    }

    /**
     * Check the boxes which are enabled in the user's musync.conf.
     *
     * @param keys The config values from the user's musync.conf.
     */
    public void importKeys(HashMap<String, String> keys) 
    {
        this.conf = keys;

        return;
    }
}
